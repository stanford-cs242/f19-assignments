open Core

exception Unimplemented

let main () =
  let rec gcd (m : int) (n : int) : int =
    if n = 0 then m
    else gcd n (m mod n)
  in

  assert (gcd 5 2 = 1);
  assert (gcd 10 2 = 2);
  assert (gcd 48 18 = 6);

  let rec fizz_buzz (n : int) : unit =
    if n > 0 then
      (fizz_buzz (n - 1);
       if n mod 3 = 0 && n mod 5 = 0 then Printf.printf "Fizzbuzz\n"
       else if n mod 3 = 0 then Printf.printf "Fizz;"
       else if n mod 5 = 0 then Printf.printf "Buzz")
    else ()
  in

  let read_line () : string =
    match In_channel.input_line In_channel.stdin with
    | Some s -> s
    | None -> assert false
  in

  let rec read_password (password : string) : unit =
    if read_line() <> password then read_password password
  in

  (* Uncomment the line below to test read_password *)
  (* let () = read_password "password" in *)

  let substring_match (pattern : string) (source : string) : int option =
    let n = String.length pattern in
    let rec aux i =
      if i + n > String.length source then None
      else if String.slice source i (i + n) = pattern then Some i
      else aux (i + 1)
    in
    aux 0
  in

  assert (substring_match "foo" "foobar" = Some 0);
  assert (substring_match "foo" "barfoo" = Some 3);
  assert (substring_match "z" "foobar" = None)

let () = main ()
