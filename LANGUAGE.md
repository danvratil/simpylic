# Language

The Simpylic language described using EBNF

```
(* Common terminals *)
new_line = ? ASCII character 0x0A ? ;
white_space = ? white space characters ? ;

(* A program consists of a series of statements separated by
   a newline character. *)
program = { statement, new_line } ;

(* This should represent all statements currently supported by
   the simpylic parser. *)
statement = 
    return_statement ;

(* This should represent all expressions currently supported by
   the simplylic parser. *)
expression = number
    | ( unary_operator, expression ) ;


return_statement = 'return', white_space, expression ;

unary_operator = "!" | "~" | "-" ;

```
