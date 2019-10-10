open Core
open Ngram_impl

let main () =

  (* Run the random generator over the input text *)
  let run (filepath : string) (ngram : int) (nwords : int) =
    (* Read input file *)
    let contents = In_channel.read_all filepath in

    (* Tokenize file contents *)
    let l = String.split contents ' ' in
    let l = List.filter_map l ~f:(fun s ->
      let s' = String.strip s in
      if String.length s' = 0 then None else Some s')
    in

    (* Build n-gram map *)
    let ngrams = compute_ngrams l ngram in
    let map = List.fold ngrams ~init:(ngram_map_new ()) ~f:ngram_map_add in
    let keys = Map.Poly.keys map in

    (* Generate sequence *)
    Random.self_init();
    let rand_init = List.nth_exn keys (Random.int (List.length keys)) in
    let str = sample_n map rand_init nwords in
    Printf.printf "%s" (String.concat ~sep:" " str)
  in

  let open Command.Param in
  let open Command.Let_syntax in
  Command.basic
    ~summary:"NGraml generator"
    [%map_open
      let filepath = anon ("filepath" %: string)
      and ngram = flag "ngram" (optional_with_default 3 int) ~doc:"Size of N-grams to analyze"
      and nwords = flag "nwords" (optional_with_default 20 int) ~doc:"Number of words to generate" in
      fun () -> run filepath ngram nwords
    ]
  |> Command.run

let () = main ()
