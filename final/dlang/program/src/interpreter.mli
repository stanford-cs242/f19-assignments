open Core
open Ast

(* Evaluates a program to a value, or an error if one occurs. *)
val eval : Program.t -> (Expr.t option, string) Result.t
