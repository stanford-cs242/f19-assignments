open Core

exception Unimplemented

type ngram = string list
type ngram_map = (ngram, string list) Map.Poly.t
type word_distribution = float String.Map.t

let rec remove_last_impl1 (l : string list) : string list =
  raise Unimplemented
;;

assert (remove_last_impl1 ["a"; "b"] = ["a"]);
;;

let remove_last_impl2 (l : string list) : string list =
  raise Unimplemented
;;

assert (remove_last_impl2 ["a"; "b"] = ["a"])
;;

let compute_ngrams (l : string list) (n : int) : string list list =
  raise Unimplemented
;;

assert (compute_ngrams ["a"; "b"; "c"] 2 = [["a"; "b"]; ["b"; "c"]]);
;;

let ngram_to_string ng =
  Printf.sprintf "[%s]" (String.concat ~sep:", " ng)
;;

let ngram_map_new () : ngram_map =
  Map.Poly.empty
;;

let ngram_map_add (map : ngram_map) (ngram : ngram) : ngram_map =
  raise Unimplemented
;;

let () =
  let map = ngram_map_new () in
  let map = ngram_map_add map ["a"; "b"] in
  (* Add your own tests here! *)
  ()
;;

let ngram_map_distribution (map : ngram_map) (ngram : ngram)
  : word_distribution option =
  raise Unimplemented
;;

let distribution_to_string (dist : word_distribution) : string =
  Sexp.to_string_hum (String.Map.sexp_of_t Float.sexp_of_t dist)
;;

let sample_distribution (dist : word_distribution) : string =
  raise Unimplemented
;;

let rec sample_n (map : ngram_map) (ng : ngram) (n : int) : string list =
  raise Unimplemented
;;
