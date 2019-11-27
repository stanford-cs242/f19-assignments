{
  open Grammar
  exception Error of string
}

rule token = parse
| "(*" _* "*)" { token lexbuf }
(* Whitespace is ignored in DLang *)
| '\n' { Lexing.new_line lexbuf ; token lexbuf }
| [' ' '\t' ] { token lexbuf }
| '(' { LPAREN }
| ')' { RPAREN }
| '[' { LBRACKET }
| ']' { RBRACKET }
| '{' { LBRACE }
| '}' { RBRACE }
| "def" { FN }
| "Vector" { VECTOR }
| "int" { TYINT }
| "float" { TYFLOAT }
| ':' { COLON }
| ';' { SEMICOLON }
| '+' { PLUS }
| '-' { SUB }
| '*' { MUL }
| '/' { DIV }
| '=' { ASSIGN }
| ',' { COMMA }
| "numrows" { BUILTIN_NUMROWS }
| "numcols" { BUILTIN_NUMCOLS }
| "addrow" { BUILTIN_ADDROW }
| "addcol" { BUILTIN_ADDCOL }
| "sum" { BUILTIN_SUM }
(* To eliminate ambiguity, symbols must be defined after other keywords *)
| ['a'-'z''A'-'Z']['a'-'z''A'-'Z''0'-'9''_']* as s { SYMBOL s }
(* To eliminate ambiguity, we must define floats before ints as the float pattern fully contains the int pattern. *)
| '-'?['0'-'9']+'.'['0'-'9']* as i { FLOAT (float_of_string i) }
| '-'?['0'-'9']+ as i { INT (int_of_string i) }
| eof { EOF }
| _ { raise (Error (Printf.sprintf "At offset %d: unexpected character.\n" (Lexing.lexeme_start lexbuf))) }
