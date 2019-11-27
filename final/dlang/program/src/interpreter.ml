open Flags
open Core
open Result.Monad_infix
open Ast
open Builtins
open Utils

exception Unreachable

type var_ctx = Expr.t String.Map.t
type func_ctx = ((symbol * Type.t) list * Stmt.t list) String.Map.t

let rec eval_expr (e : Expr.t) (vctx : var_ctx) (fctx : func_ctx)
  : (Expr.t, string) Result.t =
  match e with
  | Expr.ElemwiseBinop {binop; left; right} ->
    let b_int = (match binop with
      | Expr.Add -> (+)
      | Expr.Sub -> (-)
      | Expr.Mul -> ( * )
      | Expr.Div -> (/)) in
    let b_float = (match binop with
      | Expr.Add -> (+.)
      | Expr.Sub -> (-.)
      | Expr.Mul -> ( *. )
      | Expr.Div -> (/.)) in
    eval_expr left vctx fctx >>= fun left_val ->
    eval_expr right vctx fctx >>= fun right_val ->
    (match (left_val, right_val) with
      | (Expr.Int n1, Expr.Int n2) ->
        if binop = Expr.Div && n2 = 0 then
          Error (Printf.sprintf "Divide-by-zero error.")
        else Ok (Expr.Int (b_int n1 n2))
      (* Type coercion of int to float is performed dynamically. *)
      | (Expr.Int n1, Expr.Float n2) ->
        if binop = Expr.Div && n2 = 0.0 then
          Error (Printf.sprintf "Divide-by-zero error.")
        else Ok (Expr.Float (b_float (float_of_int n1) n2))
      | (Expr.Float n1, Expr.Int n2) ->
        if binop = Expr.Div && n2 = 0 then
          Error (Printf.sprintf "Divide-by-zero error.")
        else Ok (Expr.Float (b_float n1 (float_of_int n2)))
      | (Expr.Float n1, Expr.Float n2) ->
        if binop = Expr.Div && n2 = 0.0 then
          Error (Printf.sprintf "Divide-by-zero error.")
        else Ok (Expr.Float (b_float n1 n2))

      | (Expr.Vector v1, Expr.Vector v2) ->
        if (binop = Expr.Div && Array.mem v2 (Expr.Float 0.0)
            ~equal:(fun (Expr.Float a) (Expr.Float b) -> a = b))
        then Error (Printf.sprintf "Divide-by-zero error.")
        else
          (match Array.zip v1 v2 with
          | Some zipped -> Ok (Expr.Vector (Array.map zipped
              ~f:(fun (Expr.Float n1, Expr.Float n2) -> Expr.Float (b_float n1 n2))))
          | None -> Error (Printf.sprintf
                 "Attempted element-wise binary operation on Vectors of different sizes: %d and %d"
                 (Array.length v1) (Array.length v2)))
      | _ -> raise Unreachable)


  | Expr.RowAccessor {tensor; idx} ->
    eval_expr tensor vctx fctx >>= fun tensor_val ->
    eval_expr idx vctx fctx >>= fun row_val ->
    (match (tensor_val, row_val) with
    | (Expr.Vector col_list, Expr.Int idx) ->
      (match array_get col_list idx with
      | Some vec -> Ok vec
      | None -> Error (Printf.sprintf "Row accessor failed: out of bounds"))
    | _ -> raise Unreachable)
  | Expr.ColAccessor {tensor; idx} ->
    eval_expr tensor vctx fctx >>= fun tensor_val ->
    eval_expr idx vctx fctx >>= fun col_val ->
    (match (tensor_val, col_val) with
    | (Expr.Vector row_list, Expr.Int idx) ->
      (match array_get row_list idx with
      | Some v -> Ok v
      | None -> Error (Printf.sprintf "Row accessor failed: out of bounds"))
    | _ -> raise Unreachable)

  | Expr.Vector items ->
    let reduced = Array.map items ~f:(fun e -> eval_expr e vctx fctx) in
    let error_item = Array.find reduced ~f:(fun e -> match e with
      | Error _ -> true
      | _ -> false) in
    (match error_item with
    | Some (err) -> err
    | None -> Ok (Expr.Vector (Array.map reduced ~f:(fun e ->
      let v = Option.value_exn (Result.ok e) in
      match v with
      | Expr.Int n -> Expr.Float (float_of_int n)
      | Expr.Float _ -> v))))

  | Expr.FuncApp {name; args} ->
    let args_reduced = List.map args ~f:(fun e -> eval_expr e vctx fctx) in
    let error_elem = List.find args_reduced ~f:(fun e -> match e with
      | Error _ -> true
      | _ -> false) in
    (match error_elem with
    | Some (Error err) -> Error err
    | None -> Ok (List.map args_reduced ~f:(fun e -> Option.value_exn (Result.ok e))))
    >>= fun args_red ->
    let (arg_decls, stmt_list) = String.Map.find_exn fctx name in
    let arg_ctx = String.Map.of_alist_exn (List.zip_exn (List.map arg_decls ~f:(fun (n, _) -> n)) args_red) in
    let new_vctx = String.Map.merge vctx arg_ctx ~f:(fun ~key:_ v ->
      match v with
      | `Left v1 -> Some(v1)
      | `Both (_, v2)
      | `Right v2 -> Some(v2)
    ) in
    let final_res = List.fold stmt_list ~init:(Ok (None, new_vctx, fctx)) ~f:(fun res s ->
      (match res with
      | Ok (_, old_vctx, old_fctx) -> eval_stmt s old_vctx old_fctx
      | _ -> res)) in
    (match final_res with
    | Ok (Some e, _, _) -> Ok e
    | Ok (None, _, _) -> raise Unreachable
    | Error s -> Error s)

  | Expr.BuiltinApp {builtin; args} ->
    (match builtin with
    | Expr.Numrows -> eval_expr (List.nth_exn args 0) vctx fctx >>= fun tensor ->
      Ok (numrows tensor)
    | Expr.Numcols -> eval_expr (List.nth_exn args 0) vctx fctx >>= fun tensor ->
      Ok (numcols tensor)
    | Expr.Sum -> eval_expr (List.nth_exn args 0) vctx fctx >>= fun tensor ->
      Ok (sum tensor)
    | Expr.Addrow
    | Expr.Addcol as add ->
      eval_expr (List.nth_exn args 0) vctx fctx >>= fun tensor ->
      eval_expr (List.nth_exn args 1) vctx fctx >>= fun idx ->
      eval_expr (List.nth_exn args 2) vctx fctx >>= fun item_to_add ->
      (match add with
      | Expr.Addrow -> addrow tensor idx item_to_add
      | Expr.Addcol -> addcol tensor idx item_to_add)
    )

  | Expr.Var {name} -> Ok (String.Map.find_exn vctx name)
  | Expr.Int _ -> Ok e
  | Expr.Float _ -> Ok e

and eval_stmt (s : Stmt.t) (vctx : var_ctx) (fctx : func_ctx)
  : (Expr.t option * var_ctx * func_ctx, string) Result.t =
  match s with
  | Stmt.FuncDef {name; args; stmt_list} ->
    Ok (None, vctx, String.Map.set fctx ~key:name ~data:(args, stmt_list))
  | Stmt.VarAssign {name; value} -> eval_expr value vctx fctx >>= fun res ->
    Ok (Some res, String.Map.set vctx ~key:name ~data:res, fctx)
  | Stmt.ExprStmt e -> eval_expr e vctx fctx >>= fun res ->
    Ok (Some res, vctx, fctx)

let rec eval_prog (p : Program.t) (vctx : var_ctx) (fctx : func_ctx)
  : (Expr.t option, string) Result.t =
  match p with
  | [s] -> let res = eval_stmt s vctx fctx in
    (match res with
    | Ok (e, _, _) -> Ok e
    | Error s -> Error s)
  | s :: p_rest -> (match (eval_stmt s vctx fctx) with
    | Ok (_, new_vctx, new_fctx) -> eval_prog p_rest new_vctx new_fctx
    | Error e -> Error e)
  | [] -> Error (Printf.sprintf "Program is empty.")

let eval (p : Program.t) : (Expr.t option, string) Result.t =
  eval_prog p String.Map.empty String.Map.empty
