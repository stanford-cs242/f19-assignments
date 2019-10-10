open Core
open Option.Monad_infix

exception Unimplemented

(* Set this to true to print out intermediate state between Karel steps *)
let debug = false

type cell =
  | Empty
  | Wall
  | Beeper

type grid = cell list list

type dir =
  | North
  | West
  | South
  | East

type pos = int * int

type state = {
  karel_pos : pos;
  karel_dir : dir;
  grid : grid;
}

let get_cell (grid : grid) ((i, j) : pos) : cell option =
  (List.nth grid j) >>= fun l -> List.nth l i
;;

let set_cell (grid : grid) ((i, j) : pos) (cell : cell) : grid =
  List.mapi grid ~f:(fun j' l ->
    if j = j' then List.mapi l ~f:(fun i' c -> if i = i' then cell else c)
    else l)
;;

let state_to_string (state : state) : string =
  raise Unimplemented
;;

let empty_grid (m : int) (n : int) : grid =
  List.map (List.range 0 m) ~f:(fun _ ->
    List.map (List.range 0 n) ~f:(fun _ -> Empty))
;;

type predicate =
  | FrontIs of cell
  | NoBeepersPresent
  | Facing of dir
  | Not of predicate

type instruction =
  | Move
  | TurnLeft
  | PickBeeper
  | PutBeeper
  | While of predicate * instruction list
  | If of predicate * instruction list * instruction list

let rec predicate_to_string (pred : predicate) : string =
  match pred with
  | FrontIs c ->
    let cellstr = match c with
      | Empty -> "Empty" | Beeper -> "Beeper" | Wall -> "Wall"
    in
    Printf.sprintf "FrontIs(%s)" cellstr
  | NoBeepersPresent -> "NoBeepersPresent"
  | Facing dir ->
    let dirstr = match dir with
      | North -> "North" | South -> "South" | East -> "East" | West -> "West"
    in
    Printf.sprintf "Facing(%s)" dirstr
  | Not pred' -> Printf.sprintf "Not(%s)" (predicate_to_string pred')

let rec instruction_to_string (instr : instruction) : string =
  match instr with
  | Move -> "Move"
  | TurnLeft -> "TurnLeft"
  | PickBeeper -> "PickBeeper"
  | PutBeeper -> "PutBeeper"
  | While (pred, instrs) ->
    Printf.sprintf "While(%s, [%s])"
      (predicate_to_string pred)
      (instruction_list_to_string instrs)
  | If (pred, then_, else_) ->
    Printf.sprintf "If(%s, [%s], [%s])"
      (predicate_to_string pred)
      (instruction_list_to_string then_)
      (instruction_list_to_string else_)
and instruction_list_to_string (instrs: instruction list) : string =
  String.concat ~sep:", " (List.map ~f:instruction_to_string instrs)


let rec eval_pred (state : state) (pred : predicate) : bool =
  raise Unimplemented


let rec step (state : state) (code : instruction) : state =
  raise Unimplemented

and step_list (state : state) (instrs : instruction list) : state =
  List.fold instrs ~init:state ~f:(fun state instr ->
    if debug then
       (Printf.printf "Executing instruction %s...\n"
          (instruction_to_string instr);
        let state' = step state instr in
        Printf.printf "Executed instruction %s. New state:\n%s\n"
          (instruction_to_string instr)
          (state_to_string state');
        state')
     else
       step state instr)

;;

let checkers_algo : instruction list = [
]
