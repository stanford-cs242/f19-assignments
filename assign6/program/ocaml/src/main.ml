open Core
open Result.Monad_infix

let main () =
  let open Slang in
  let p_basic : prog = [
    {name = "main"; params = []; body = [
       Return (String "basic")
     ]}
  ] in
  let p_concat : prog = [
    {name = "main"; params = []; body = [
       Assign ("x", String "hello");
       Return (Concat (Var "x", String " world"))
     ]}
  ] in
  let p_funcall : prog = [
    {name = "foo"; params = ["x"]; body = [
       Return (Concat (Var "x", String " world"))
     ]};
    {name = "main"; params = []; body = [
       Assign ("x", String "hello");
       Assign ("y", Var "x");
       Return (Call ("foo", [Var "y"]))
     ]}
  ] in
  let p_overused_var : prog = [
    {name = "foo"; params = ["x"]; body = [
       Return (Concat (Var "x", Var "x"))
     ]};
    {name = "main"; params = []; body = [
       Assign ("x", String "hello");
       Assign ("y", Var "x");
       Return (Call ("foo", [Var "y"]))
     ]}
  ] in
  let p_unused_var : prog = [
    {name = "main"; params = []; body = [
       Assign ("x", String "hello")
     ]}
  ] in
  let p_undeclared_var : prog = [
    {name = "foo"; params = ["x"]; body = [
      Return (Var "y")
     ]};
    {name = "main"; params = []; body = [
       Assign ("x", String "hello");
       Assign ("y", Var "x");
       Return (Call ("foo", [Var "y"]))
     ]}
  ] in

  let test_typecheck (p : prog) (name : string) : bool =
    match typecheck p with
    | Ok () ->
      let wp = Translate.translate p in
      let path = ("../wasm/src/" ^ name ^ ".wat") in
      Printf.printf "Wrote program `%s` to path %s\n" name path;
      Out_channel.write_all path ~data:(Wasm.module_to_string wp);
      true
    | Error s ->
      Printf.printf "Program `%s` failed to type check: %s\n" name s;
      false
  in
  assert (test_typecheck p_basic "basic");
  assert (test_typecheck p_concat "concat");
  assert (test_typecheck p_funcall "funcall");
  assert (not (test_typecheck p_overused_var "overused_var"));
  assert (not (test_typecheck p_unused_var "unused_var"));
  assert (not (test_typecheck p_undeclared_var "undeclared_var"))



let _ = main ()
