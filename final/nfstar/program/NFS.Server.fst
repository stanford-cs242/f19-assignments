module NFS.Server

open FStar.Exn
open FStar.All
open FStar.OrdSet
open FStar.OrdMap
open FStar.Ref
open FStar.String
open FStar.List.Tot

(** Define the basic types in the system. **)
type id = int

type user_id = id

type file_id = int

type file_name = string

type file_path = list file_name

type data = string

type file_handle = int

type is_dir = bool

type permission =
  | Open
  | Read
  | Write
  | AttrModify

let permission_to_num x =
  match x with
  | Open -> 0
  | Read -> 1
  | Write -> 2
  | AttrModify -> 3

let permission_cmp (x : permission) (y : permission) =
  (permission_to_num x) <= (permission_to_num y)

type permission_map =
  ordmap id (ordset permission permission_cmp) (<=)


noeq type system_state = {
  users : ordset user_id (<=);
  file_paths : ordmap file_id (file_path * is_dir) (<=);
  file_contents : ordmap file_id data (<=);
  file_permissions : ordmap file_id permission_map (<=);
  file_handles : ordmap file_handle (file_id * user_id) (<=);
}

(** Create the system state. **)

private val system : ref system_state
private let getFreshSystemState () = {
  users = OrdSet.empty;
  file_paths = OrdMap.empty;
  file_contents = OrdMap.empty;
  file_permissions = OrdMap.empty;
  file_handles = OrdMap.empty;
}
private let system = ST.alloc (getFreshSystemState ())

(** General helper functions. **)

(* Convert path into a string. *)
let pathToString (file_path : file_path) =
  "/" ^ (String.concat "/" file_path)

(* Get file ID associated with the given path. *)
private val getFileId' : system_state -> file_path -> Tot (option file_id)
private let getFileId' (s : system_state) (file_path : file_path) =
  let file_paths = s.file_paths in
  let keys = OrdMap.dom file_paths in
  OrdSet.fold (fun acc key ->
    match OrdMap.select key file_paths with
    | Some (f, _) -> if f = file_path then Some key else acc
    | None -> acc
  ) None keys

private val getFileId : file_path -> ST (option file_id)
  (requires (fun h -> True)) (ensures (fun h x h' -> True))
private let getFileId file_path =
  getFileId' !system file_path


(* Convert list to ordset. *)
let intListToSet (l : list int) : Tot (ordset int (<=)) =
  List.Tot.fold_left (fun acc e -> OrdSet.union (OrdSet.singleton e) acc)
    OrdSet.empty l

(* Convert ordset to list. *)
let intSetToList (s : ordset int (<=)) : Tot (list int) =
  OrdSet.fold (fun acc e -> e :: acc) [] s

(* Implement bind...F* doesn't have this built-in. *)
let (>>=) (#a : Type) (#b : Type) (o : option a) (f : a -> ML (option b)) =
  match o with
  | Some v -> f v
  | None -> None
(* Tot version of bind for pure uses. *)
let (>>>=) (#a : Type) (#b : Type) (o : option a) (f : a -> Tot (option b)) =
  match o with
  | Some v -> f v
  | None -> None

let unwrap_bool (inp : option bool) =
  match inp with
  | Some b -> b
  | None -> false

(** User operations. **)

(* Public add user function. *)
val addUser : (user_id : user_id) -> ST unit
  (requires (fun h -> True)) (ensures (fun h x h' -> True))
let addUser user_id = system :=
  { !system with users = OrdSet.union (OrdSet.singleton user_id) (!system).users }

let removeUser user_id = system :=
  { !system with users = OrdSet.remove user_id (!system).users }

let setUsers users = system :=
  { !system with users = users }

let getUsers () = (!system).users


(** File operations. **)

private let getFreshFileId () =
  let keys = OrdMap.dom (!system).file_paths in
  OrdSet.fold (fun new_file_id file_id ->
    if file_id = new_file_id then file_id + 1 else new_file_id
  ) 0 keys

private let getFreshFileHandle () =
  let keys = OrdMap.dom (!system).file_handles in
  OrdSet.fold (fun new_fh fh -> if fh = new_fh then fh + 1 else new_fh) 0 keys

(* Set attribute for user and file (internal). *)
private let setAttr file_path user_id permission =
  let _ =
    getFileId file_path >>= (fun file_id ->
    OrdMap.select file_id (!system).file_permissions >>= (fun file_permissions_map ->
    let user_permissions_map =
      match OrdMap.select user_id file_permissions_map with
      | Some m -> m
      | None -> OrdSet.empty
    in
    let user_permissions_map' =
      OrdSet.union (OrdSet.singleton permission) user_permissions_map in
    let file_permissions_map' =
      OrdMap.update user_id user_permissions_map' file_permissions_map in
    let file_permissions' =
      OrdMap.update file_id file_permissions_map' (!system).file_permissions in
    system := { !system with file_permissions = file_permissions' };
    Some ()))
  in ()

(* Policy that file exists. *)
private let fileExists (s : system_state) (f : file_path) =
  match getFileId' s f with
  | Some file_id -> (
    OrdMap.contains file_id s.file_paths &&
    OrdMap.contains file_id s.file_contents &&
    OrdMap.contains file_id s.file_permissions)
  | None -> false
private type fileExists_t f h =
  fileExists (Ref.sel h system) f == true

(* Create file.
 *
 * Requires that file does not already exist.
 *)
private val createFile' : (f : file_path) -> is_dir -> ST unit
  (requires (fun h -> ~(fileExists_t f h)))
  (ensures (fun h x h' -> True))
private let createFile' file_path is_dir =
  let file_id = getFreshFileId () in
  let s = !system in
  system := { s with
    file_paths = OrdMap.update file_id (file_path, is_dir) s.file_paths;
    file_contents = OrdMap.update file_id "" s.file_contents;
    file_permissions = OrdMap.update file_id OrdMap.empty s.file_permissions;
  }

(* Create file if it does not exist. *)
private val createFile : file_path -> user_id -> is_dir -> All unit
  (requires (fun h -> True)) (ensures (fun h x h' -> True))
private let createFile file_path user_id is_dir =
  (* Create the file if it does not already exist. *)
  if fileExists !system file_path
  then failwith "file already exists"
  else createFile' file_path is_dir;

  (* Grant root and user all permissions to the file. *)
  let users = (intSetToList (intListToSet [0; user_id])) in
  List.iter (fun user ->
    List.iter (fun permission ->
      setAttr file_path user_id permission
    ) [Open; Read; Write; AttrModify]
  ) users

(* Called once to initialize the server. *)
let startServer users =
  (* Reset server state. *)
  system := getFreshSystemState ();

  (* Create the root user (ID 0). *)
  addUser 0;
  (* Add all other users to the system. *)
  List.iter (fun user_id -> addUser user_id) users;

  (* Create the root file object (dir), under root user. *)
  createFile [] 0 true;
  (* Give all users permission to open root. *)
  List.iter (fun user_id -> setAttr [] user_id Open) users;


  ()

(* Policy that user has given permission on the file path. *)
private let userHasPermission s id file_path permission : Tot bool =
  unwrap_bool (
    getFileId' s file_path >>>= (fun file_id ->
    OrdMap.select file_id s.file_permissions >>>= (fun file_permissions_map ->
    OrdMap.select id file_permissions_map >>>= (fun user_permissions_map ->
    Some (OrdSet.mem permission user_permissions_map)))))
private type userHasPermission_t uid fp p h =
  userHasPermission (Ref.sel h system) uid fp p == true

(* Open file.
 *
 * Require user has open permission on the file path.
 *)
private val openInternal : file_handle -> (user_id : user_id) -> (file_path : file_path) -> All unit
  (requires (fun h -> userHasPermission_t user_id file_path Open h))
  (ensures (fun h x h' -> True))
private let openInternal (fh : file_handle) (user_id : user_id) (file_path : file_path) =
  let _ = getFileId file_path >>= (fun file_id ->
    system :=
      { !system with file_handles = OrdMap.update fh (file_id, user_id) (!system).file_handles };
    Some ())
  in ()

val nfsOpen : file_handle -> file_name -> id -> bool -> All file_handle
  (requires (fun h -> True)) (ensures (fun h x h' -> True))
let nfsOpen parent_fh file_name id create_file =
  let parent_file_id = match OrdMap.select parent_fh (!system).file_handles with
    | Some (file_id, file_user_id) ->
      if id = file_user_id then file_id
      else failwith "OPEN: parent file handle does not belong to user"
    | None -> failwith "OPEN: parent file handle not found"
  in
  let parent_file_path = match OrdMap.select parent_file_id (!system).file_paths with
    | Some (file_path, is_dir) ->
      if is_dir then file_path
      else failwith "OPEN: parent file handle does not refer to directory"
    | None -> failwith "OPEN: parent file handle does not map to a valid path"
  in
  let file_path = List.rev (file_name :: (List.rev parent_file_path)) in
  if create_file then createFile file_path id false else ();
  let fh = getFreshFileHandle () in
  if userHasPermission !system id file_path Open
  then (openInternal fh id file_path; fh)
  else failwith "OPEN: user does not have permission to open file"

(* Mount root directory for the user. *)
val nfsMount : user_id -> All file_handle
  (requires (fun h -> True)) (ensures (fun h x h' -> True))
let nfsMount user_id =
  let fh = getFreshFileHandle () in
  let root_file_path = [] in
  if userHasPermission !system user_id root_file_path Open
  then (openInternal fh user_id root_file_path; fh)
  else failwith "user does not have permission to mount"
