open Flags
open Core

exception Unimplemented

let fresh s = s ^ "'"

module Type = struct
  open Ast.Type

  let rec substitute_map (rename : t String.Map.t) (tau : t) : t =
    match tau with
    | Num -> Num
    (* Add more cases here! *)
    | _ -> raise Unimplemented

  let substitute (x : string) (tau' : t) (tau : t) : t =
    substitute_map (String.Map.singleton x tau') tau

  let rec to_debruijn (tau : t) : t =
    let rec aux (depth : int String.Map.t) (tau : t) : t =
      match tau with
      | Num -> Num
      (* Add more cases here! *)
      | _ -> raise Unimplemented
    in
    aux String.Map.empty tau

  let rec aequiv (tau1 : t) (tau2 : t) : bool =
    let rec aux (tau1 : t) (tau2 : t) : bool =
      match (tau1, tau2) with
      | (Num, Num) -> true
      | (Bool, Bool) | (Unit, Unit) -> true
      | (Var x, Var y) -> x = y
      | (Fn x, Fn y) -> aux x.arg y.arg && aux x.ret y.ret
      | (Sum x, Sum y) -> aux x.left y.left && aux x.right y.right
      | (Product x, Product y) -> aux x.left y.left && aux x.right y.right
      | (Rec x, Rec y) -> aux x.tau y.tau
      | (Forall x, Forall y) -> aux x.tau y.tau
      | (Exists x, Exists y) -> aux x.tau y.tau
      | _ -> false
    in
    aux (to_debruijn tau1) (to_debruijn tau2)

  let inline_tests () =
    let p = Parser.parse_type_exn in

    assert (
      aequiv
        (substitute "a" (p "num") (p "forall b . a"))
        (p "forall a . num"));
    assert (
      aequiv
        (substitute "a" (p "b") (p "forall b . a"))
        (p "forall c . b"));
    assert (
      not (aequiv
        (substitute "a" (p "b") (p "forall b . a"))
        (p "forall b . b")));
    assert (
      aequiv
        (substitute "a" (p "b") (p "forall b . forall b . a"))
        (p "forall q . forall c . b"));
    assert (
      not (aequiv
        (substitute "a" (p "b") (p "forall b . forall b . a"))
        (p "forall a . forall b . a")));

    assert (aequiv (p "forall a . a") (p "forall b . b"));
    assert (not (aequiv (p "forall a . a") (p "forall b . num")));
    assert (aequiv
              (p "forall a . forall b . a -> b")
              (p "forall x . forall y . x -> y"))

  (* Uncomment the line below when you want to run the inline tests. *)
  (* let () = inline_tests () *)
end

module Expr = struct
  open Ast.Expr

  let rec substitute_map (rename : t String.Map.t) (e : t) : t =
    match e with
    | Num _ -> e
    | Binop {binop; left; right} -> Binop {
      binop;
      left = substitute_map rename left;
      right = substitute_map rename right}
    (* Put more cases here! *)
    | _ -> raise Unimplemented

  let substitute (x : string) (e' : t) (e : t) : t =
    substitute_map (String.Map.singleton x e') e

  let rec to_debruijn (e : t) : t =
    let rec aux (depth : int String.Map.t) (e : t) : t =
      match e with
      | Num _ -> e
      | Binop {binop; left; right} -> Binop {
        binop; left = aux depth left; right = aux depth right}
      (* Add more cases here! *)
      | _ -> raise Unimplemented
    in
    aux String.Map.empty e

  let aequiv (e1 : t) (e2 : t) : bool =
    let rec aux (e1 : t) (e2 : t) : bool =
      match (e1, e2) with
      | (Num n1, Num n2) -> n1 = n2
      | (Var x, Var y) -> x = y
      | (Binop l, Binop r) ->
        l.binop = r.binop && aux l.left r.left && aux l.right r.right
      | (True, True) | (False, False) -> true
      | (If l, If r) ->
        aux l.cond r.cond && aux l.then_ r.then_ && aux l.else_ r.else_
      | (Relop l, Relop r) ->
        l.relop = r.relop && aux l.left r.left && aux l.right r.right
      | (And l, And r) ->
        aux l.left r.left && aux l.right r.right
      | (Or l, Or r) ->
        aux l.left r.left && aux l.right r.right
      | (Lam l, Lam r) ->
        aux l.e r.e
      | (App l, App r) ->
        aux l.lam r.lam && aux l.arg r.arg
      | (Unit, Unit) -> true
      | (Pair l, Pair r) ->
        aux l.left r.left && aux l.right r.right
      | (Project l, Project r) ->
        aux l.e r.e && l.d = r.d
      | (Inject l, Inject r) ->
        aux l.e r.e && l.d = r.d
      | (Case l, Case r) ->
        aux l.e r.e && aux l.eleft r.eleft && aux l.eright r.eright
      | (Fix l, Fix r) -> aux l.e r.e
      | (TyLam l, TyLam r) ->
        aux l.e r.e
      | (TyApp l, TyApp r) -> aux l.e r.e
      | (Fold_ l, Fold_ r) -> aux l.e r.e
      | (Unfold l, Unfold r) -> aux l r
      | (Export l, Export r) -> aux l.e r.e
      | (Import l, Import r) -> aux l.e_mod r.e_mod && aux l.e_body r.e_body
      | _ -> false
    in
    aux (to_debruijn e1) (to_debruijn e2)

  let inline_tests () =
    let p = Parser.parse_expr_exn in
    let t1 = p "(fun (x : num) -> x) y" in
    assert (aequiv (substitute "x" (Num 0) t1) t1);
    assert (aequiv (substitute "y" (Num 0) t1)
              (p "(fun (x : num) -> x) 0"));

    let t2 = p "x + (fun (x : num) -> y)" in
    assert (aequiv
              (substitute "x" (Num 0) t2)
              (p "0 + (fun (x : num) -> y)"));
    assert (aequiv (substitute "y" (Num 0) t2)
              (p "x + (fun (x : num) -> 0)"));

    assert (aequiv (p "fun (x : num) -> x") (p "fun (y : num) -> y"));

    assert (not (aequiv (p "fun (x : num) -> fun (x : num) -> x + x")
                   (p "fun (x : num) -> fun (y : num) -> y + x")));

    assert (
      aequiv
        (p "tyfun a -> fun (x : a) -> x")
        (p "tyfun b -> fun (x : b) -> x"));

    ()

  (* Uncomment the line below when you want to run the inline tests. *)
  (* let () = inline_tests () *)
end
