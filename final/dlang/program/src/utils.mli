open Core
open Ast

(* Put any helpful subroutines here to keep your code clean. *)

(* Gets an element from an Array given an index.
   Returns Some if index is valid, otherwise returns None. *)
val array_get : 'a array -> int -> 'a option

