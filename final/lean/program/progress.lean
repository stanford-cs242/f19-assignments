import .arith
import .inversion

-- Propositions used in the reference solution:
-- val.DNat, or.intro_right, val_inversion, exists.elim, apply_binop, steps.*

-- Tactics used in the reference solution:
-- intros, induction, cases, case, apply, exact simp, existsi

theorem progress : ∀ e : Expr, val e ∨ (∃ e', e ↦ e') :=
  sorry -- Remove this line and add your proof
