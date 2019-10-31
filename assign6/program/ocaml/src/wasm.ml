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

let concat = String.concat ~sep:" "

let instr_to_string i =
  match i with
  | Binop `Add -> "i32.add"
  | Binop `Sub -> "i32.sub"
  | Binop `Mul -> "i32.mul"
  | Const n -> Printf.sprintf "i32.const %d" n
  | Store -> "i32.store"
  | Load -> "i32.load"
  | Call s -> Printf.sprintf "call $%s" s
  | SetLocal s -> Printf.sprintf "set_local $%s" s
  | GetLocal s -> Printf.sprintf "get_local $%s" s
  | SetGlobal s -> Printf.sprintf "set_global $%s" s
  | GetGlobal s -> Printf.sprintf "get_global $%s" s
  | Return -> "return"
  | Drop -> "drop"

let change_mem (i : instr) : instr list =
  match i with
  | Store -> [SetLocal "store"; Const 4; Binop `Mul; GetLocal "store"; Store]
  | Load -> [Const 4; Binop `Mul; Load]
  | _ -> [i]

let func_to_string f =
  Printf.sprintf
    "(func $%s %s (result i32) %s (local $store i32) %s) (export \"%s\" (func $%s))"
    f.name
    (concat (List.map ~f:(fun p -> Printf.sprintf "(param $%s i32)" p) f.params))
    (concat (List.map ~f:(fun p -> Printf.sprintf "(local $%s i32)" p) f.locals))
    (concat (List.map ~f:change_mem f.body |> List.concat |>
             (List.map ~f:(fun i -> Printf.sprintf "(%s)" (instr_to_string i)))))
    f.name
    f.name

let module_to_string m =
  let imports = {|
  (import "wasm-alloc" "alloc" (func $alloc (param i32) (result i32)))
  (import "wasm-alloc" "dealloc" (func $dealloc (param i32)))
  (import "memcpy" "memcpy" (func $memcpy (param i32) (param i32) (param i32)))
  (import "memcpy" "memory" (memory 0))
  (global $length (mut i32) (i32.const 0))
|} in
  Printf.sprintf "(module %s %s)"
    imports
    (String.concat ~sep:" " (List.map ~f:func_to_string m))
