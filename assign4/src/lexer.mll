{
  open Grammar
  exception Error of string
}

rule token = parse
| "(*" _* "*)" { token lexbuf }
| '\n' { Lexing.new_line lexbuf ; token lexbuf }
| [' ' '\t' ] { token lexbuf }
| '.' { DOT }
| '(' { LPAREN }
| ')' { RPAREN }
| '[' { LBRACKET }
| ']' { RBRACKET }
| 'R' { RIGHT }
| 'L' { LEFT }
| "fun" { FN }
| "num" { TY_NUM }
| "bool" { TY_BOOL }
| "->" { ARROW }
| ":" { COLON }
| '+' { PLUS }
| '-' { SUB }
| ',' { COMMA }
| "as" { AS }
| "inj" { INJECT }
| '*' { MUL }
| '/' { DIV }
| '=' { EQ }
| '>' { GT }
| '<' { LT }
| "&&" { AND }
| "||" { OR }
| "if" { IF }
| "then" { THEN }
| "else" { ELSE }
| "fold" { FOLD }
| "unfold" { UNFOLD }
| "export" { EXPORT }
| "import" { IMPORT }
| "without" { WITHOUT }
| "true" { TRUE }
| "false" { FALSE }
| "let" { LET }
| "letrec" { LETREC }
| "in" { IN }
| "tyfun" { TFN }
| "forall" { FORALL }
| "exists" { EXISTS }
| "rec" { REC }
| "unit" { TY_UNIT }
| '|' { BAR }
| '{' { LBRACE }
| '}' { RBRACE }
| "case" { CASE }
| ['a'-'z''A'-'Z']['a'-'z''A'-'Z''0'-'9''_']* as v { VAR v }
| ['0'-'9']+ as i { NUM (int_of_string i) }
| '-'['0'-'9']+ as i { NUM (int_of_string i) }
| eof { EOF }
| _ { raise (Error (Printf.sprintf "At offset %d: unexpected character.\n" (Lexing.lexeme_start lexbuf))) }
