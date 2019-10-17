module Type : sig
  open Ast.Type

  val to_debruijn : t -> t

  val aequiv : t -> t -> bool

  val substitute : string -> t -> t -> t
end

module Expr : sig
  open Ast.Expr

  val to_debruijn : t -> t

  val aequiv : t -> t -> bool

  val type_substitute : string -> Ast.Type.t -> t -> t

  val substitute : string -> t -> t -> t
end
