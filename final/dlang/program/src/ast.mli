 open Core

type symbol = string
[@@deriving sexp_of, sexp, compare]

module Type : sig
  type t =
    | Int
    | Float
    | Vector
    | Fn of {args : t list; ret : t}
  [@@deriving variants, sexp_of, sexp, compare]

  val to_string : t -> string

  val to_string_sexp : t -> string
end

module Expr : sig
  type elemwise_binop = Add | Sub | Mul | Div
  [@@deriving variants, sexp_of, sexp, compare]


  type builtin_func = Numrows | Numcols | Addrow | Addcol | Sum
  [@@deriving variants, sexp_of, sexp, compare]

  type t =
    | ElemwiseBinop of {binop : elemwise_binop; left : t; right : t}

    | RowAccessor of {tensor : t; idx : t}
    | ColAccessor of {tensor : t; idx : t}

    | Vector of t array

    | FuncApp of {name: symbol ; args: t list}
    | BuiltinApp of {builtin: builtin_func ; args: t list}

    | Var of {name: symbol}
    | Int of int
    | Float of float
  [@@deriving variants, sexp_of, sexp, compare]

  val to_string : t -> string

  val to_string_sexp : t -> string
end

module Stmt : sig
  type t =
    | FuncDef of {name: symbol ; args: (symbol * Type.t) list ; stmt_list: t list}
    | VarAssign of {name : symbol ; value : Expr.t}
    | ExprStmt of Expr.t
  [@@deriving variants, sexp_of, sexp, compare]

  val to_string : t -> string

  val to_string_sexp : t -> string
end

module Program : sig
  type t = Stmt.t list
  [@@deriving sexp_of, sexp, compare]

  val to_string : t -> string

  val to_string_sexp : t -> string
end
