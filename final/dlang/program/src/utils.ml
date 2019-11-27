open Core
open Ast

let array_get (arr : 'a array) (i : int) : 'a option =
  if i >= 0 && i < Array.length arr
  then Some (Array.get arr i)
  else None

