%{
  open Ast
%}

%token <string> VAR
%token EOF
%token ARROW
%token DOT
%token FN
%token LBRACKET
%token RBRACKET
%token LPAREN
%token RPAREN
%token COLON
%token PLUS
%token SUB
%token MUL
%token DIV
%token GT
%token LT
%token EQ
%token AND
%token OR
%token IF
%token THEN
%token ELSE
%token TRUE
%token FALSE
%token AS
%token LET
%token LETREC
%token EXPORT
%token IMPORT
%token WITHOUT
%token FOLD
%token UNFOLD
%token IN
%token TFN
%token INJECT
%token RIGHT
%token LEFT
%token FORALL
%token EXISTS
%token REC
%token RBRACE
%token LBRACE
%token COMMA
%token BAR
%token CASE
%token TY_NUM
%token TY_BOOL
%token TY_UNIT
%token <int> NUM

%right TyLam
%left TyProd TySum

%right ExLam ExUnfold ExTfn
%right ExLet
%left AND OR
%left LT GT EQ
%left PLUS SUB
%left MUL DIV

%start <Ast.Expr.t> expr_toplevel
%start <Ast.Type.t> type_toplevel

%%

expr_toplevel:
| e = expr EOF { e }

type_toplevel:
| t = ty EOF { t }

expr:
| lam = expr arg = expr2 { Expr.App { lam ; arg } }
| e = expr2 { e }

expr2:
| left = expr2 binop = binop right = expr2
  { Expr.Binop { binop ; left ; right } }
| left = expr2 relop = relop right = expr2
  { Expr.Relop { relop ; left ; right }  }
| left = expr2 AND right = expr2 { Expr.And { left ; right } }
| left = expr2 OR right = expr2 { Expr.Or { left ; right } }
| FN LPAREN x = VAR COLON tau = ty RPAREN ARROW e = expr
  { Expr.Lam { x ; tau ; e } } %prec ExLam
| n = NUM { Expr.Num(n) }
| v = VAR { Expr.Var(v) }
| TRUE { Expr.True }
| FALSE { Expr.False }
| LPAREN left = expr2 COMMA right = expr2 RPAREN { Expr.Pair { left ; right } }
| e = expr2 DOT d = dir { Expr.Project { e ; d } }
| INJECT e = expr2 EQ d = dir AS tau = ty { Expr.Inject { e ; d ; tau } }
| CASE e = expr2 LBRACE LEFT LPAREN xleft = VAR RPAREN ARROW eleft = expr2 BAR RIGHT LPAREN xright = VAR RPAREN ARROW eright = expr2 RBRACE
  { Expr.Case { e ; xleft; eleft; xright; eright } }
| IF cond = expr2 THEN then_ = expr2 ELSE else_ = expr2
  { Expr.If { cond; then_; else_ } }
| LET x = VAR COLON tau = ty EQ evar = expr2 IN ebody = expr2
  { Expr.App { lam = Expr.Lam { x ; tau ; e = ebody } ; arg = evar } } %prec ExLet
| LETREC x = VAR COLON tau = ty EQ evar = expr2 IN ebody = expr2
  { Expr.App { lam = Expr.Lam {x ; tau ; e = ebody} ;
               arg = Expr.Fix { x ; tau ; e = evar } } } %prec ExLet
| TFN a = VAR ARROW e = expr2 { Expr.TyLam { a ; e } } %prec ExTfn
| e = expr2 LBRACKET tau = ty RBRACKET { Expr.TyApp { e ; tau } }
| FOLD e = expr2 AS tau = ty { Expr.Fold_ { e; tau } }
| UNFOLD e = expr2 { Expr.Unfold e } %prec ExUnfold
| EXPORT e = expr2 WITHOUT tau_adt = ty AS tau_mod = ty
  { Expr.Export { e; tau_adt; tau_mod } }
| IMPORT LPAREN x = VAR COMMA a = VAR RPAREN EQ e_mod = expr2 IN e_body = expr2
  { Expr.Import { x; a; e_mod; e_body } }
| LPAREN RPAREN { Expr.Unit }
| LPAREN e = expr RPAREN { e }

%inline binop:
| PLUS { Expr.Add }
| SUB { Expr.Sub }
| MUL { Expr.Mul }
| DIV { Expr.Div }

%inline relop:
| EQ { Expr.Eq }
| GT { Expr.Gt }
| LT { Expr.Lt }

ty:
| REC a = VAR DOT tau = ty { Type.Rec { a; tau } }
| FORALL a = VAR DOT tau = ty { Type.Forall { a; tau } }
| EXISTS a = VAR DOT tau = ty { Type.Exists { a; tau } }
| t = ty2 { t }

ty2:
| TY_NUM { Type.Num }
| TY_BOOL { Type.Bool }
| TY_UNIT { Type.Unit }
| a = VAR { Type.Var a }
| left = ty2 PLUS right = ty2 { Type.Sum { left; right } } %prec TySum
| left = ty2 MUL right = ty2 { Type.Product { left; right } } %prec TyProd
| arg = ty2 ARROW ret = ty2 { Type.Fn { arg; ret } } %prec TyLam
| LPAREN t = ty RPAREN { t }

dir:
| LEFT {Expr.Left}
| RIGHT {Expr.Right}
