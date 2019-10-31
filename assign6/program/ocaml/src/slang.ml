open Core
open Result.Monad_infix

type expr =
  | String of string
  | Concat of expr * expr
  | Var of string
  | Call of string * expr list

type stmt =
  | Assign of string * expr
  | Return of expr

type func = {name: string; params: string list; body: stmt list}

type prog = func list

let rec typecheck_expr
          (fn_map : string list String.Map.t)
          (var_set : String.Set.t)
          (e : expr)
  : (unit, string) Result.t =
  let tc = typecheck_expr fn_map in
  match e with
  | String _ -> Ok ()

  | Concat (e1, e2) ->
    tc var_set e1 >>= fun () -> tc var_set e2

  | Var x ->
    if String.Set.mem var_set x then
      Ok ()
    else
      Error (Printf.sprintf "Variable %s is undefined or moved" x)

  | Call (x, args) ->
    List.fold args ~init:(Ok ())
      ~f:(fun res arg ->
        res >>= fun () -> tc var_set arg)
    >>= fun () ->
    (match String.Map.find fn_map x with
     | Some expected_args ->
       if List.length expected_args = List.length args then Ok ()
       else Error (Printf.sprintf
                     "List was given %d parameters, expected %d parameters"
                     (List.length expected_args) (List.length args))
     | None -> Error (Printf.sprintf "Called undefined function %s" x))

let typecheck_func (fn_map : string list String.Map.t) (f : func)
  : (unit, string) Result.t =
  List.fold f.body
    ~init:((Ok (String.Set.of_list f.params)))
    ~f:(fun var_set_res s ->
      var_set_res >>= fun var_set ->
      (match s with
       | Assign (x, e) ->
         typecheck_expr fn_map var_set e
         >>| fun () -> String.Set.add var_set x
       | Return e ->
         typecheck_expr fn_map var_set e
         >>| fun () -> var_set))
  >>| fun _ -> ()

let typecheck (p : prog) : (unit, string) Result.t =
  let fn_map =
    String.Map.of_alist_exn (List.map p ~f:(fun f -> (f.name, f.params)))
  in
  List.fold p
    ~init:(Ok ())
    ~f:(fun acc f -> acc >>= fun () -> typecheck_func fn_map f)
