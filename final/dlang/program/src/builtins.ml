open Core
open Ast

exception Unreachable

let numcols (tensor : Expr.t) : Expr.t =
  match tensor with
  | Expr.Vector items -> Expr.Int (Array.length items)
  | _ -> raise Unreachable

let numrows (tensor : Expr.t) : Expr.t =
  match tensor with
  | Expr.Vector items -> Expr.Int (Array.length items)
  | _ -> raise Unreachable
