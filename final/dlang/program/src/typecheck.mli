open Core
open Ast

(* Returns nothing if the program typechecks, otherwise provides an error. *)
val typecheck : Program.t -> (unit, string) Result.t
