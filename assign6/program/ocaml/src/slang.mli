open Core

type expr =
  | String of string
  | Concat of expr * expr
  | Var of string
  | Call of string * expr list

type stmt =
  | Assign of string * expr
  | Return of expr

type func = {name: string; params: string list; body: stmt list}

type prog = func list

val typecheck : prog -> (unit, string) Result.t
