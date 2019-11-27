open Core
open Result.Monad_infix
open Ast

type var_ctx = Type.t String.Map.t
type func_ctx = Type.t String.Map.t

let rec typecheck_expr (e : Expr.t) (vctx : var_ctx) (fctx : func_ctx)
  : (Type.t, string) Result.t =
  match e with
  | Expr.ElemwiseBinop {left; right; _} ->
    typecheck_expr left vctx fctx >>= fun tau_left ->
    typecheck_expr right vctx fctx >>= fun tau_right ->
    (match (tau_left, tau_right) with
     | (Type.Int, Type.Int) -> Ok Type.Int
     (* All ints are coerced to floats when binop'ed with a float. *)
     | (Type.Int, Type.Float)
     | (Type.Float, Type.Int)
     | (Type.Float, Type.Float) -> Ok Type.Float

     | (Type.Vector, Type.Vector) -> Ok Type.Vector
     | _ -> Error (Printf.sprintf
         "Binary operands have incompatible types: (%s : %s) and (%s : %s)"
         (Expr.to_string left) (Type.to_string tau_left)
         (Expr.to_string right) (Type.to_string tau_right)))


  | Expr.RowAccessor {tensor; idx}
  | Expr.ColAccessor {tensor; idx} ->
    typecheck_expr tensor vctx fctx >>= fun tau_tensor ->
    typecheck_expr idx vctx fctx >>= fun tau_idx ->
    (match (tau_tensor, tau_idx) with
     | (Type.Vector, Type.Int) -> Ok Type.Float
     | _ -> Error (Printf.sprintf
         "Row/Column accessors can only be applied on Vectors using int indices. You have: (%s : %s) and (%s : %s)"
         (Expr.to_string tensor) (Type.to_string tau_tensor)
         (Expr.to_string idx) (Type.to_string tau_idx)))


  | Expr.Vector items ->
    (* In lieu of having a bind operator for a list of Results, we use
       check_item to ensure the item typechecks and is a numerical type. *)
    let check_item (item) =
      (let tau_item = typecheck_expr item vctx fctx in
       match tau_item with
       | Ok t -> t = Type.Int || t = Type.Float
       | Error _ -> false)
    in if Array.for_all items ~f:check_item
    then Ok Type.Vector
    else Error (Printf.sprintf
      "Vector has an element that does not typecheck to a numerical type (int or float).")

  | Expr.FuncApp {name; args} -> (match String.Map.find fctx name with
    | Some ty ->
      (match ty with
      | Type.Fn {args = tau_args; ret = tau_ret} ->
        (match List.zip args tau_args with
        | Some zipped ->
          let check_item ((item, expected_tau)) =
            (match typecheck_expr item vctx fctx with
             | Ok tau_item -> tau_item = expected_tau
             | Error _ -> false)
          in (match List.for_all zipped ~f:check_item with
          | true -> Ok tau_ret
          | _ -> Error (Printf.sprintf
              "Function %s was given an improperly typed argument." name))
        | None -> Error (Printf.sprintf
               "Function %s expected %d args but was given %d."
               name (List.length tau_args) (List.length args)))
      | _ -> Error (Printf.sprintf "Symbol %s is not a function" name))
    | None -> Error (Printf.sprintf "Unbound function %s" name))

  | Expr.BuiltinApp {builtin; args} ->
    (match builtin with
    | Expr.Numrows
    | Expr.Numcols ->
      if List.length args <> 1
      then Error (Printf.sprintf
        "Builtin numrows/numcols expected 1 argument but got %d args."
        (List.length args))
      else typecheck_expr (List.nth_exn args 0) vctx fctx >>= fun tau_tensor ->
      (match tau_tensor with
      | Type.Vector -> Ok Type.Int
      | _ -> Error (Printf.sprintf
          "Expected type Vector for builtin numrows/numcols but got %s"
          (Type.to_string tau_tensor)))

    | Expr.Addrow
    | Expr.Addcol ->
      if List.length args <> 3
      then Error (Printf.sprintf
        "Builtin addrow/addcol expected 3 arguments but got %d args"
        (List.length args))
      else typecheck_expr (List.nth_exn args 0) vctx fctx >>= fun tau_tensor ->
      typecheck_expr (List.nth_exn args 1) vctx fctx >>= fun tau_idx ->
      typecheck_expr (List.nth_exn args 2) vctx fctx >>= fun tau_elem ->
      (match (tau_tensor, tau_idx, tau_elem) with
      | (Type.Vector, Type.Int, Type.Int)
      | (Type.Vector, Type.Int, Type.Float) -> Ok Type.Vector
      | _ -> Error (Printf.sprintf
          "Expected types (Vector, int, num) for builtin addrow/addcol, but got (%s, %s, %s)"
          (Type.to_string tau_tensor) (Type.to_string tau_idx)
          (Type.to_string tau_elem)))
    | Expr.Sum ->
      if List.length args <> 1
      then Error (Printf.sprintf
        "Builtin sum expected 1 argument but got %d args."
        (List.length args))
      else typecheck_expr (List.nth_exn args 0) vctx fctx >>= fun tau_tensor ->
      (match tau_tensor with
      | Type.Vector -> Ok Type.Float
      | _ -> Error (Printf.sprintf
          "Expected type Vector for builtin sum but got %s"
          (Type.to_string tau_tensor)))
    )

  | Expr.Int _ -> Ok Type.Int
  | Expr.Float _ -> Ok Type.Float
  | Expr.Var {name} -> (match String.Map.find vctx name with
    | Some tau_var -> Ok tau_var
    | None -> Error (Printf.sprintf "Unbound variable %s" name))

let rec typecheck_stmt (stmt : Stmt.t) (vctx : var_ctx) (fctx : func_ctx)
  : (var_ctx * func_ctx * Type.t option, string) Result.t =
  match stmt with
  | Stmt.FuncDef {name; args = arg_decls; stmt_list} ->
    let uniq_names = String.Set.of_list (List.map arg_decls ~f:(fun (n, _) -> n)) in
    if String.Set.length uniq_names <> List.length arg_decls
    then Error (Printf.sprintf "Found a duplicate argument name in function declaration for %s" name)
    else let new_vctx = (List.fold arg_decls ~init:vctx ~f:(fun vctx_old (n, t) ->
      String.Map.set vctx_old ~key:n ~data:t)) in
    let final_res = List.fold stmt_list ~init:(Ok (new_vctx, fctx, None)) ~f:(fun res s ->
      (match res with
      | Ok (vctx_old, fctx, _) -> typecheck_stmt s vctx_old fctx
      | _ -> res))
    in (match final_res with
    | Ok (_, _, ty) -> let tau_func = Type.Fn {
        args = (List.map arg_decls ~f:(fun (_, t) -> t));
        ret = Option.value_exn ty } in
      let new_fctx = String.Map.add fctx ~key:name ~data:tau_func in
      (match new_fctx with
      | `Ok new_fctx -> Ok (vctx, new_fctx, None)
      | `Duplicate -> Error (Printf.sprintf "Function symbol %s is repeated" name))
    | _ -> final_res)
  | Stmt.VarAssign {name; value} -> typecheck_expr value vctx fctx >>= fun tau_value ->
      Ok ((String.Map.set vctx ~key:name ~data:tau_value), fctx, (Some tau_value))
  | Stmt.ExprStmt expr -> typecheck_expr expr vctx fctx >>= fun tau_expr ->
      Ok (vctx, fctx, (Some tau_expr))

let rec typecheck_prog (prog: Program.t) (vctx : var_ctx) (fctx : func_ctx)
  : (var_ctx * func_ctx * Type.t option, string) Result.t =
  match prog with
  | s :: prog_rest -> (match (typecheck_stmt s vctx fctx) with
    | Ok (vctx_new, fctx_new, _) -> typecheck_prog prog_rest vctx_new fctx_new
    | Error e -> Error e)
  | [] -> Ok (vctx, fctx, None)

let typecheck prog =
  let res = typecheck_prog prog String.Map.empty String.Map.empty in
  match res with
  | Ok _ -> Ok ()
  | Error e -> Error e
