open Flags
open Core
open Result.Monad_infix
open Ast

let interpret (expr : Expr.t) =
  (if verbose () then Printf.printf "Expr: %s\n\n" (
     Expr.to_string (if testing () then Ast_util.Expr.to_debruijn expr else expr)));
  Typecheck.typecheck expr >>= fun ty ->
  (if verbose () then Printf.printf "Type: %s\n\n" (
     Type.to_string (if testing () then Ast_util.Type.to_debruijn ty else ty)));
  Interpreter.eval expr

let run (filepath : string) =
  let input = In_channel.read_all filepath in
  let result = Parser.parse_expr input >>= interpret in
  match result with
  | Ok e -> Printf.printf "Success: %s\n" (Expr.to_string (
    if testing () then Ast_util.Expr.to_debruijn e else e))
  | Error s -> Printf.printf "Error: %s\n" s

let main () =
  let open Command.Let_syntax in
  Command.basic
    ~summary:"Lam1 interpreter"
    [%map_open
      let filepath = anon ("filepath" %: string)
      and verbose = flag "v" no_arg ~doc:"Print verbose information"
      and extra_verbose = flag "vv" no_arg ~doc:"Print extra verbose information"
      and testing = flag "t" no_arg ~doc: "Print all outputs in format required for test harness" in
      fun () ->
        set_verbose (verbose || extra_verbose);
        set_extra_verbose extra_verbose;
        set_testing testing;
        run filepath
    ]
  |> Command.run

let () = main ()
