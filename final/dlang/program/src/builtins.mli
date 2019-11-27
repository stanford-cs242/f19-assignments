open Core
open Ast

(* Returns the number of elements in a Vector or rows in a Matrix. *)
val numrows : Expr.t -> Expr.t
(* Returns the number of elements in a Vector or columns in a Matrix. *)
val numcols : Expr.t -> Expr.t
(* Returns the sum of all elements in a Vector or a Matrix. *)
val sum : Expr.t -> Expr.t

(* Adds an element at the provided position to a Vector, or adds a Vector
   as a row at the provided row number to a Matrix. *)
val addrow : Expr.t -> Expr.t -> Expr.t -> (Expr.t, string) Result.t
(* Adds an element at the provided position to a Vector, or adds a Vector
   as a col at the provided row number to a Matrix. *)
val addcol : Expr.t -> Expr.t -> Expr.t -> (Expr.t, string) Result.t

