open Core
open Ast

(* Returns the number of elements in a Vector or rows in a Matrix. *)
val numrows : Expr.t -> Expr.t
(* Returns the number of elements in a Vector or columns in a Matrix. *)
val numcols : Expr.t -> Expr.t
