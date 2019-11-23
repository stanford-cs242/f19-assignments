inductive Binop | Add | Sub | Mul | Div
example : Binop := Binop.Add


inductive Expr
| Num : ℕ → Expr
| Binop : Binop → Expr → Expr → Expr

example : Expr := Expr.Num 1
example : Expr := Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)


inductive val : Expr → Prop
| DNat (n : ℕ) : val (Expr.Num n)

example : val (Expr.Num 2) := val.DNat 2


def apply_binop (op : Binop) (nl nr : ℕ) : ℕ :=
  Binop.cases_on op (nl + nr) (nl - nr) (nl * nr) (nl / nr)

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

notation e `↦`:35 e' := steps e e'

example : (Expr.Binop Binop.Add (Expr.Num 1) (Expr.Num 2)) ↦ (Expr.Num 3) :=
   steps.DOp Binop.Add 1 2
