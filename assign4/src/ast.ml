open Core

type variable = string
[@@deriving sexp_of, sexp, compare]

module Type = struct
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

  let rec to_string ty =
    match ty with
    | Num -> "num"
    | Bool -> "bool"
    | Unit -> "unit"
    | Var x -> x
    | Fn {arg; ret} ->
      Printf.sprintf "(%s -> %s)" (to_string arg) (to_string ret)
    | Product {left; right} ->
      Printf.sprintf "(%s * %s)" (to_string left) (to_string right)
    | Sum {left; right} ->
      Printf.sprintf "(%s + %s)" (to_string left) (to_string right)
    | Rec {a; tau} ->
      Printf.sprintf "μ %s . %s" a (to_string tau)
    | Forall {a; tau} ->
      Printf.sprintf "∀ %s . %s" a (to_string tau)
    | Exists {a; tau} ->
      Printf.sprintf "∃ %s . %s" a (to_string tau)

  let to_string_sexp ty =
    Sexp.to_string_hum (sexp_of_t ty)
end

module Expr = struct
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

  let rec to_string e =
    match e with
    | Num n -> string_of_int n
    | Binop {binop; left; right} ->
      let bstr = match binop with
          Add -> "+" | Sub -> "-" | Mul -> "*" | Div -> "/"
      in
      Printf.sprintf "(%s %s %s)" (to_string left) bstr (to_string right)
    | Relop {relop; left; right} ->
      let rstr = match relop with
          Eq -> "=" | Lt -> "<" | Gt -> ">"
      in
      Printf.sprintf "(%s %s %s)" (to_string left) rstr (to_string right)
    | True -> "true"
    | False -> "false"
    | If {cond; then_; else_} ->
      Printf.sprintf "(if %s then %s else %s)"
        (to_string cond) (to_string then_) (to_string else_)
    | And {left; right} ->
      Printf.sprintf "(%s && %s)" (to_string left) (to_string right)
    | Or {left; right} ->
      Printf.sprintf "(%s || %s)" (to_string left) (to_string right)
    | Var x -> x
    | Lam {x; tau; e} ->
      Printf.sprintf "(fun (%s : %s) -> %s)"
        x (Type.to_string tau) (to_string e)
    | App {lam; arg} ->
      Printf.sprintf "(%s %s)" (to_string lam) (to_string arg)
    | Unit -> "()"
    | Pair {left; right} ->
      Printf.sprintf "(%s, %s)" (to_string left) (to_string right)
    | Project {e; d} ->
      let dstr = match d with Left -> "L" | Right -> "R" in
      Printf.sprintf "%s.%s" (to_string e) dstr
    | Inject {e; d; tau} ->
      let dstr = match d with Left -> "L" | Right -> "R" in
      Printf.sprintf "(inj %s = %s as %s)"
        (to_string e) dstr (Type.to_string tau)
    | Case {e; xleft; eleft; xright; eright} ->
      Printf.sprintf "(case %s {L(%s) -> %s | R(%s) -> %s)"
        (to_string e) xleft (to_string eleft) xright (to_string eright)
    | Fix {x; tau; e} ->
      Printf.sprintf "(fix (%s : %s) -> %s)"
        x (Type.to_string tau) (to_string e)
    | TyLam {a; e} ->
      Printf.sprintf "(Λ %s -> %s)" a (to_string e)
    | TyApp {e; tau} ->
      Printf.sprintf "(%s [%s])" (to_string e) (Type.to_string tau)
    | Fold_ {e; tau} ->
      Printf.sprintf "(fold %s as %s)" (to_string e) (Type.to_string tau)
    | Unfold e ->
      Printf.sprintf "(unfold %s)" (to_string e)
    | Export {e; tau_adt; tau_mod} ->
      Printf.sprintf "(export %s without %s as %s)"
        (to_string e) (Type.to_string tau_adt) (Type.to_string tau_mod)
    | Import {x; a; e_mod; e_body} ->
      Printf.sprintf "(import (%s, %s) = %s in %s)"
        x a (to_string e_mod) (to_string e_body)

  let to_string_sexp e =
    Sexp.to_string_hum (sexp_of_t e)
end
