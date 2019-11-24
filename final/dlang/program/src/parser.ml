open Core
open Ast

exception Parse_failure of string

let parse f input =
  let filebuf = Lexing.from_string input in
  try (Ok (f Lexer.token filebuf)) with
  | Lexer.Error msg -> Error msg
  | Grammar.Error ->
    let start_pos = Lexing.lexeme_start_p filebuf in
    let end_pos = Lexing.lexeme_end_p filebuf in
    Error (
      Printf.sprintf "Parse error: line %d, characters %d-%d"
        start_pos.pos_lnum
        (start_pos.pos_cnum - start_pos.pos_bol)
        (end_pos.pos_cnum - end_pos.pos_bol))

let parse_exn f input =
  match parse f input with
  | Ok e -> e
  | Error s -> raise (Parse_failure s)


let parse_expr = parse Grammar.prog
let parse_expr_exn = parse_exn Grammar.prog
