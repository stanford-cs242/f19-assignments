import .arith

@[simp]
lemma val_inversion : ∀ e : Expr, val e → ∃ n : ℕ, e = Expr.Num n :=
  sorry -- Remove this line and add your proof
