import .arith

inductive evals : Expr → Expr → Prop
| Val (e : Expr) : evals e e
| Step (e e_step e_val: Expr) :
  (e ↦ e_step) → evals e_step e_val → evals e e_val

notation e `↦*`:35 e' := evals e e'

example : (Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)) ↦* (Expr.Num 3) :=
  evals.Step
    (Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2))
    (Expr.Num 3)
    (Expr.Num 3)
    (steps.DOp Binop.Add 1 2)
    (evals.Val (Expr.Num 3))

example : (Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)) ↦* (Expr.Num 3) :=
  begin
    apply evals.Step,
    show Expr, from Expr.Num 3,
    exact steps.DOp Binop.Add 1 2,
    exact evals.Val (Expr.Num 3)
  end

@[refl]
lemma evals_refl (e : Expr) : e ↦* e := evals.Val e

@[trans]
lemma evals_trans (e1 e2 e3 : Expr) (h1 : e1 ↦* e2) (h2 : e2 ↦* e3)
  : e1 ↦* e3 :=
  begin
    induction h1,
    case evals.Val { assumption },
    case evals.Step {
      apply evals.Step,
      show Expr, from h1_e_step,
      assumption,
      exact h1_ih h2
    }
  end

lemma transitive_left (b : Binop) (el el' er : Expr) :
  (el ↦* el') → (Expr.Binop b el er ↦* Expr.Binop b el' er) :=
  begin
    sorry -- Remove this line and add your proof
  end

lemma transitive_right (b : Binop) (el er er' : Expr) :
  val el → (er ↦* er') → (Expr.Binop b el er ↦* Expr.Binop b el er') :=
  begin
    sorry -- Remove this line and add your proof
  end
