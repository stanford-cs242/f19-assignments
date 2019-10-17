let _verbose : bool ref = ref false
let verbose () = !_verbose
let set_verbose b = _verbose := b

let _extra_verbose : bool ref = ref false
let extra_verbose () = !_extra_verbose
let set_extra_verbose b = _extra_verbose := b

let _testing : bool ref = ref false
let testing () = !_testing
let set_testing b = _testing := b
