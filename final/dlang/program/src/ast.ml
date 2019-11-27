open Core

type symbol = string
[@@deriving sexp_of, sexp, compare]

module Type = struct
  type t =
    | Int
    | Float
    | Vector
    | Fn of {args : t list; ret : t}
  [@@deriving variants, sexp_of, sexp, compare]

  let rec to_string ty =
    match ty with
    | Int -> "int"
    | Float -> "float"
    | Vector -> "Vector"
    | Fn {args; ret} ->
      Printf.sprintf "(%s) -> %s" (String.concat ~sep:", " (List.map args
        ~f:to_string)) (to_string ret)

  let to_string_sexp ty =
    Sexp.to_string_hum (sexp_of_t ty)
end

module Expr = struct
  type elemwise_binop = Add | Sub | Mul | Div
  [@@deriving variants, sexp_of, sexp, compare]


  type builtin_func = Numrows | Numcols | Addrow | Addcol | Sum
  [@@deriving variants, sexp_of, sexp, compare]

  type t =
    | ElemwiseBinop of {binop : elemwise_binop ; left : t ; right : t}

    | RowAccessor of {tensor : t ; idx : t}
    | ColAccessor of {tensor : t ; idx : t}

    | Vector of t array

    | FuncApp of {name: symbol ; args: t list}
    | BuiltinApp of {builtin: builtin_func ; args: t list}

    | Var of {name: symbol}
    | Int of int
    | Float of float
  [@@deriving variants, sexp_of, sexp, compare]

  let rec to_string e =
    match e with
    | ElemwiseBinop {binop; left; right} ->
      let bstr = match binop with
        Add -> "+" | Sub -> "-" | Mul -> "*" | Div -> "/"
      in
      Printf.sprintf "(%s %s %s)" (to_string left) bstr (to_string right)
    | RowAccessor {tensor; idx} ->
      Printf.sprintf "%s[%s,]" (to_string tensor) (to_string idx)
    | ColAccessor {tensor; idx} ->
      Printf.sprintf "%s[,%s]" (to_string tensor) (to_string idx)
    | Vector items ->
      Printf.sprintf "Vector[%s]" (String.concat ~sep:", " (Array.to_list
        (Array.map items ~f:to_string)))
    | FuncApp {name; args} ->
      Printf.sprintf "%s(%s)" name (String.concat ~sep:", " (List.map args
        ~f:to_string))
    | BuiltinApp {builtin; args} ->
      let bstr = match builtin with
        | Numrows -> "numrows" | Numcols -> "numcols"
        | Addrow -> "addrow" | Addcol -> "addcol"
        | Sum -> "sum"
      in
      Printf.sprintf "%s(%s)" bstr (String.concat ~sep:", " (List.map args
        ~f:to_string))
    | Var {name} -> name
    | Int n -> string_of_int n
    | Float n -> string_of_float n

  let to_string_sexp e =
    Sexp.to_string_hum (sexp_of_t e)
end

module Stmt = struct
  type t =
    | FuncDef of {name: symbol ; args: (symbol * Type.t) list ; stmt_list: t list}
    | VarAssign of {name : symbol ; value : Expr.t}
    | ExprStmt of Expr.t
  [@@deriving variants, sexp_of, sexp, compare]

  let rec to_string e =
    match e with
    | FuncDef {name; args; stmt_list; _} ->
      let arg_decl_to_string ((name, ty)) = Printf.sprintf "%s: %s" name
        (Type.to_string ty) in
      Printf.sprintf "def %s(%s) {\n\t%s\n}" name
        (String.concat ~sep:", " (List.map args ~f:arg_decl_to_string))
        (String.concat ~sep:"\n\t" (List.map stmt_list ~f:to_string))
    | VarAssign {name; value; _} ->
      Printf.sprintf "%s = %s;" name (Expr.to_string value)
    | ExprStmt expr ->
      Printf.sprintf "%s;" (Expr.to_string expr)

  let to_string_sexp e =
    Sexp.to_string_hum (sexp_of_t e)
end

module Program = struct
  type t = Stmt.t list
  [@@deriving sexp_of, sexp, compare]

  let to_string e =
    Printf.sprintf "%s" (String.concat ~sep:"\n" (List.map e ~f:Stmt.to_string))

  let to_string_sexp e =
    Sexp.to_string_hum (sexp_of_t e)
end

