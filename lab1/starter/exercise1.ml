open Core

exception Unimplemented

let main () =
  let rec gcd (m : int) (n : int) : int =
    raise Unimplemented
  in

  assert (gcd 5 2 = 1);
  assert (gcd 10 2 = 2);
  assert (gcd 48 18 = 6);

  let rec fizz_buzz (n : int) : unit =
    raise Unimplemented
  in

  let read_line () : string =
    match In_channel.input_line In_channel.stdin with
    | Some s -> s
    | None -> assert false
  in

  let rec read_password (password : string) : unit =
    raise Unimplemented
  in

  (* Uncomment the line below to test read_password *)
  (* let () = read_password "password" in *)

  let substring_match (pattern : string) (source : string) : int option =
    raise Unimplemented
  in

  assert (substring_match "foo" "foobar" = Some 0);
  assert (substring_match "foo" "barfoo" = Some 3);
  assert (substring_match "z" "foobar" = None)

let () = main ()
