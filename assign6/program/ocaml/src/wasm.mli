open Core

type instr =
  | Binop of [`Add | `Sub | `Mul]
  | Const of int
  | Store
  | Load
  | Call of string
  | SetLocal of string
  | GetLocal of string
  | SetGlobal of string
  | GetGlobal of string
  | Return
  | Drop

type func = {name: string; params: string list; locals: string list; body: instr list}

type module_ = func list

val module_to_string : module_ -> string
