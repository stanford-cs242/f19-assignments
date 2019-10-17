open Core
open Ast

type outcome =
  | Step of Expr.t
  | Val

(* Attempts to execute a small step in the term. *)
val trystep : Expr.t -> outcome

(* Reduces a term to a value, or an error if one occurs. *)
val eval : Expr.t -> (Expr.t, string) Result.t
