let _stop_at_parser : bool ref = ref false
let stop_at_parser () = !_stop_at_parser
let set_stop_at_parser b = _stop_at_parser := b

let _stop_at_typechecker : bool ref = ref false
let stop_at_typechecker () = !_stop_at_typechecker
let set_stop_at_typechecker b = _stop_at_typechecker := b
