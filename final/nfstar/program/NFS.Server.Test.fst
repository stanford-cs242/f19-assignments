module NFS.Server.Test

open FStar.All
open FStar.Exn

open NFS.Server

type all_unit = unit -> All unit (requires (fun h -> True)) (ensures (fun h x h' -> True))

(** Runtime assertions. **)

(* Assert that condition is true. *)
let rassert cond failmsg =
  if cond then () else failwith failmsg

(* Assert that exception occurred. *)
let rassert_exn (f : all_unit) failmsg =
  let failed = try f (); false with | _ -> true in
  rassert failed failmsg

(** Test user operations. **)

let testUserOperations () : All unit (requires (fun h -> True)) (ensures (fun h x h' -> True)) =
  (* Reset users for the tests. *)
  let initial_users = getUsers() in
  setUsers (intListToSet []);
  rassert (getUsers() = intListToSet []) "users not empty";

  (* Add users. *)
  addUser 1;
  rassert (getUsers() = intListToSet [1]) "users not 1";
  addUser 2;
  rassert (getUsers() = intListToSet [1; 2]) "users not 1,2";
  addUser 3;
  rassert (getUsers() = intListToSet [1; 2; 3]) "users not 1,2,3";

  (* Remove users. *)
  removeUser 2;
  rassert (getUsers() = intListToSet [1; 3]) "users not 1,3";
  removeUser 3;
  rassert (getUsers() = intListToSet [1]) "users not 1";
  removeUser 1;
  rassert (getUsers() = intListToSet []) "users not empty";

  (* Set users. *)
  setUsers (intListToSet [1; 2; 3]);
  rassert (getUsers() = intListToSet [1; 2; 3]) "users not 1,2,3";

  ()

(** Test file operations. **)

let testNfsOpen () : All unit (requires (fun h -> True)) (ensures (fun h x h' -> True)) =
  let curr_fh = 0 in

  (* Test mounting server. *)
  let root1 = nfsMount 1 in
  rassert (root1 = curr_fh) "root1 wrong";
  let curr_fh = curr_fh + 1 in
  let root2 = nfsMount 2 in
  rassert (root2 = curr_fh) "root2 wrong";
  let curr_fh = curr_fh + 1 in
  let root3 = nfsMount 3 in
  rassert (root3 = curr_fh) "root3 wrong";
  let curr_fh = curr_fh + 1 in

  (* Test that exceptions raised on bad inputs to nfsMount/nfsOpen. *)
  rassert_exn (fun () -> let _ = nfsMount 100 in ())
    "non-existent user mount";
  rassert_exn (fun () -> let _ = nfsOpen 100 "foo" 0 true in ())
    "bad parent file handle";
  rassert_exn (fun () -> let _ = nfsOpen root2 "foo" 1 true in ())
    "parent file handle does not belong to user";
  rassert_exn (fun () -> let _ = nfsOpen root1 "foo" 1 false in ())
    "file does not exist";

  (* Test no exceptions thrown on good inputs, correct handles are returned. *)
  rassert (nfsOpen root1 "foo" 1 true = curr_fh)
    "/foo cannot be opened by root1";
  let curr_fh = curr_fh + 1 in
  rassert (nfsOpen root2 "bar" 2 true = curr_fh)
    "/bar cannot be opened by root2";
  let curr_fh = curr_fh + 1 in

  (* Ensure duplicate files cannot be created. *)
  rassert_exn (fun () -> let _ = nfsOpen root1 "foo" 1 true in ())
    "same file created twice";

  (* Opening existing file (not creating), ensure we get a new handle back. *)
  rassert (nfsOpen root1 "foo" 1 false = curr_fh)
    "/foo cannot be opened by root1";
  let curr_fh = curr_fh + 1 in

  (* Make sure user 2 cannot open user 1's file. *)
  rassert_exn (fun () -> let _ = nfsOpen root2 "foo" 2 false in ())
    "/foo was opened by user 2 that does not have permission to open";


  ()

(** Test runner. **)

let runTests () =
  let system_users : list user_id = [1; 2; 3; 4; 5; 6; 7; 8; 9; 10] in
  let tests : list all_unit = [
    testUserOperations;
    testNfsOpen;
  ]
  in
  List.iter (fun (test : all_unit) ->
    startServer system_users;
    test ()
  ) tests

let main =
  runTests ();
  FStar.IO.print_string "Tests Passed!\n"
