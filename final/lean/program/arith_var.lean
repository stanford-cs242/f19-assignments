inductive Binop | Add | Sub | Mul | Div
example : Binop := Binop.Add


inductive Expr
| Num : ℕ → Expr
| Binop : Binop → Expr → Expr → Expr
-- Fill in Let and Var syntax

example : Expr := Expr.Num 1
example : Expr := Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)


inductive val : Expr → Prop
| DNat (n : ℕ) : val (Expr.Num n)

example : val (Expr.Num 2) := val.DNat 2


def apply_binop (op : Binop) (nl nr : ℕ) : ℕ :=
  Binop.cases_on op (nl + nr) (nl - nr) (nl * nr) (nl / nr)

inductive subst : ℕ → Expr → Expr → Expr → Prop
| SNum (i n : ℕ) (e' : Expr) : subst i e' (Expr.Num n) (Expr.Num n)
| SBinop (op : Binop) (i : ℕ) (el er el' er' e' : Expr) :
  subst i e' el el' → subst i e' er er' →
  subst i e' (Expr.Binop op el er) (Expr.Binop op el' er')
-- Fill in remaining substitution rules

inductive steps : Expr → Expr → Prop
| DLeft (op : Binop) (el el' er : Expr) :
  steps el el' →
  steps
    (Expr.Binop op el er)
    (Expr.Binop op el' er)
| DRight (op : Binop) (el er er' : Expr) :
  steps er er' → val el →
  steps
    (Expr.Binop op el er)
    (Expr.Binop op el er')
| DOp (op: Binop) (nl nr : ℕ) :
  steps
    (Expr.Binop op (Expr.Num nl) (Expr.Num nr))
    (Expr.Num (apply_binop op nl nr))
-- Fill in D-Let step rule

notation e `↦`:35 e' := steps e e'

example : (Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)) ↦ (Expr.Num 3) :=
   steps.DOp Binop.Add 1 2

inductive valid : ℕ → Expr → Prop
| TNum (n i : ℕ) :
  valid i (Expr.Num n)
| TBinop (op : Binop) (el er : Expr) (i : ℕ) :
  valid i el → valid i er → valid i (Expr.Binop op el er)
-- Fill in T-Let and T-Var rules


lemma subst_preserves_valid :
  ∀ (e e' esub : Expr), ∀ (i : ℕ),
    valid (i+1) e → valid i e' → subst i e' e esub → valid i esub :=
  begin
  sorry -- Remove this line and add your proof
end

theorem preservation :
  ∀ e e' : Expr, (e ↦ e') → valid 0 e → valid 0 e' :=
  begin
    sorry -- Remove this line and add your proof
  end

