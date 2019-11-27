%{
  open Ast
%}

/* These tokens are defined in the lexer.mll file. */
%token LPAREN
%token RPAREN
%token LBRACKET
%token RBRACKET
%token LBRACE
%token RBRACE
%token FN
%token VECTOR
%token TYINT
%token TYFLOAT
%token BUILTIN_NUMROWS
%token BUILTIN_NUMCOLS
%token BUILTIN_ADDROW
%token BUILTIN_ADDCOL
%token BUILTIN_SUM
%token COLON
%token SEMICOLON
%token PLUS
%token SUB
%token MUL
%token DIV
%token ASSIGN
%token COMMA
%token <string> SYMBOL
%token <int> INT
%token <float> FLOAT
%token EOF

/* Associativity/precedence of tokens is defined here. */
%left PLUS SUB
%left MUL DIV

/* Starting point for parser is from the rule labeled `prog`, with the result being cast to a Program.t. */
%start <Ast.Program.t> prog

%%

prog:
| stmt_list = stmt* EOF { stmt_list }
;

arg_decl:
| name = SYMBOL COLON ty = non_func_type { (name, ty) }
;

arg_decls_list:
| al = separated_list(COMMA, arg_decl) { al }
;

stmt:
| FN name = SYMBOL LPAREN args = arg_decls_list RPAREN LBRACE stmt_list = non_func_stmt+ RBRACE
  { Stmt.FuncDef { name ; args ; stmt_list} }
| stmt = non_func_stmt { stmt }
;

/* Functions cannot include function declarations inside them.
   These statements are permissible for use in a function. */
non_func_stmt:
| name = SYMBOL ASSIGN value = expr SEMICOLON
  { Stmt.VarAssign { name ; value } }
| expr = expr SEMICOLON { Stmt.ExprStmt(expr) }
;

/* Yes, you can put vanilla OCaml in the braces! */
vec_items:
| vi = separated_list(COMMA, expr) { Array.of_list vi }
;


args_list:
| al = separated_list(COMMA, expr) { al }
;

expr:
| left = expr binop = elemwise_binop right = expr
  { Expr.ElemwiseBinop { binop ; left ; right } }
| tensor = expr LBRACKET idx = expr COMMA RBRACKET
  { Expr.RowAccessor { tensor ; idx } }
| tensor = expr LBRACKET COMMA idx = expr RBRACKET
  { Expr.ColAccessor { tensor ; idx } }
| VECTOR LBRACKET vi = vec_items RBRACKET
  { Expr.Vector vi }
| builtin = builtin_func LPAREN args = args_list RPAREN
  { Expr.BuiltinApp {builtin ; args } }
| name = SYMBOL LPAREN args = args_list RPAREN
  { Expr.FuncApp {name ; args } }
| name = SYMBOL { Expr.Var { name } }
| n = INT { Expr.Int(n) }
| n = FLOAT { Expr.Float(n) }
| LPAREN e = expr RPAREN { e }
;

%inline elemwise_binop:
| PLUS { Expr.Add }
| SUB { Expr.Sub }
| MUL { Expr.Mul }
| DIV { Expr.Div }


non_func_type:
| TYINT { Type.Int }
| TYFLOAT { Type.Float }
| VECTOR { Type.Vector }
;

builtin_func:
| BUILTIN_NUMROWS { Expr.Numrows }
| BUILTIN_NUMCOLS { Expr.Numcols }
| BUILTIN_ADDROW { Expr.Addrow }
| BUILTIN_ADDCOL { Expr.Addcol }
| BUILTIN_SUM { Expr.Sum }
;
