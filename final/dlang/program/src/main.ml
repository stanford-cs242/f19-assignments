open Flags
open Core
open Result.Monad_infix
open Ast

let parse (filepath : string) =
  let input = In_channel.read_all filepath in
  let result = Parser.parse_expr input in
  match result with
  | Ok p -> Printf.printf "SUCCESS:\n%s\n" (Program.to_string p)
  | Error s -> Printf.printf "PARSE ERROR: %s\n" s

let typecheck (filepath: string) =
  let input = In_channel.read_all filepath in
  let parse_result = Parser.parse_expr input in
  match parse_result with
  | Ok p -> let type_result = Typecheck.typecheck p in
    (match type_result with
    | Ok _ -> Printf.printf "SUCCESS"
    | Error s -> Printf.printf "TYPE ERROR: %s\n" s)
  | Error s -> Printf.printf "PARSE ERROR: %s\n" s

let interpret (filepath: string) =
  let input = In_channel.read_all filepath in
  let parse_result = Parser.parse_expr input in
  match parse_result with
  | Ok p -> let type_result = Typecheck.typecheck p in
    (match type_result with
    | Ok _ -> let eval_result = Interpreter.eval p in
      (match eval_result with
      | Ok (Some e) -> Printf.printf "SUCCESS: %s\n" (Expr.to_string e)
      | Ok (None) -> Printf.printf "SUCCESS: No output."
      | Error s -> Printf.printf "EVAL ERROR: %s\n" s)
    | Error s -> Printf.printf "TYPE ERROR: %s\n" s)
  | Error s -> Printf.printf "PARSE ERROR: %s\n" s

let main () =
  let open Command.Let_syntax in
  Command.basic
    ~summary:"DL Compiler"
    [%map_open
      let filepath = anon ("filepath" %: string)
      and stop_at_parser = flag "lp" no_arg ~doc:"Run lexer and parser only"
      and stop_at_typechecker = flag "t" no_arg ~doc:"Run lexer, parser, and typechecker only" in
      fun () ->
        set_stop_at_parser stop_at_parser;
        set_stop_at_typechecker stop_at_typechecker;
        if stop_at_parser then
          parse filepath
        else if stop_at_typechecker then
          typecheck filepath
        else
          interpret filepath
    ]
  |> Command.run

let () = main ()
