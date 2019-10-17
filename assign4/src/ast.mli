open Core

type variable = string
[@@deriving sexp_of, sexp, compare]

module Type : sig
  type t =
    | Num
    | Bool
    | Unit
    | Var of variable
    | Fn of {arg : t ; ret : t}
    | Product of {left : t ; right : t}
    | Sum of {left : t ; right : t}
    | Rec of {a : variable ; tau : t}
    | Forall of {a : variable ; tau : t}
    | Exists of {a : variable ; tau : t}
  [@@deriving variants, sexp_of, sexp, compare]

  val to_string : t -> string

  val to_string_sexp : t -> string
end

module Expr : sig
  type binop = Add | Sub | Mul | Div
  [@@deriving variants, sexp_of, sexp, compare]

  type relop = Lt | Gt | Eq
  [@@deriving variants, sexp_of, sexp, compare]

  type direction = Left | Right
  [@@deriving variants, sexp_of, sexp, compare]

  type t =
    | Num of int
    | Binop of {binop : binop; left : t; right : t}

    | True | False
    | If of {cond : t; then_ : t; else_ : t}
    | Relop of {relop : relop; left : t; right : t}
    | And of {left : t; right : t}
    | Or of {left : t; right : t}

    | Var of variable
    | Lam of {x : variable; tau : Type.t; e : t}
    | App of {lam : t; arg : t}

    | Unit
    | Pair of {left : t; right : t}
    | Project of {e : t; d : direction}

    | Inject of {e : t; d : direction; tau : Type.t}
    | Case of {e : t; xleft : variable; eleft: t; xright : variable; eright : t}

    | Fix of {x : variable; tau : Type.t; e : t}

    | TyLam of {a : variable; e : t}
    | TyApp of {e : t; tau : Type.t}

    | Fold_ of {e : t; tau : Type.t}
    | Unfold of t

    | Export of {e : t; tau_adt : Type.t; tau_mod : Type.t}
    | Import of {x : variable; a : variable; e_mod : t; e_body : t}
  [@@deriving variants, sexp_of, sexp, compare]

  val to_string : t -> string
end
