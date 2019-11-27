open Core
open Ast
open Utils

exception Unreachable

let numcols (tensor : Expr.t) : Expr.t =
  match tensor with
  | Expr.Vector items -> Expr.Int (Array.length items)
  | _ -> raise Unreachable

let numrows (tensor : Expr.t) : Expr.t =
  match tensor with
  | Expr.Vector items -> Expr.Int (Array.length items)
  | _ -> raise Unreachable

let sum (tensor : Expr.t) : Expr.t =
  match tensor with
  | Expr.Vector items -> Expr.Float (Array.fold items ~init:0. ~f:(fun a n ->
    match n with Expr.Float i -> a +. i))
  | _ -> raise Unreachable

let addrow (tensor : Expr.t) (idx : Expr.t) (item_to_add : Expr.t)
: (Expr.t, string) Result.t =
  match (tensor, idx, item_to_add) with
  | (Expr.Vector items, Expr.Int n, Expr.Float f) ->
    let old_len = Array.length items in
    if n < 0 || n > old_len
    then Error (Printf.sprintf "Expected 0 <= idx <= %d for builtin addrow/addcol, but got %d"
      old_len n)
    else let new_arr = Array.create ~len:(old_len + 1) (Expr.Float 0.) in
    Array.blit ~src:items ~src_pos:0 ~dst:new_arr ~dst_pos:0 ~len:n;
    new_arr.(n) <- (Expr.Float f);
    Array.blit ~src:items ~src_pos:n ~dst:new_arr ~dst_pos:(n+1) ~len:(old_len - n);
    Ok (Expr.Vector new_arr)
  | _ -> raise Unreachable

let addcol (tensor : Expr.t) (idx : Expr.t) (item_to_add : Expr.t)
: (Expr.t, string) Result.t =
  match (tensor, idx, item_to_add) with
  | (Expr.Vector _, _, _) -> addrow tensor idx item_to_add
  | _ -> raise Unreachable

