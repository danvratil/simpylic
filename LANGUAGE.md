# Language

The Simpylic language described using EBNF

```
(* Common terminals *)
new_line = ? ASCII character 0x0A ? ;
white_space = ? white space characters ? ;
identifier = ? [a-zA-Z]\w* ? ;

(* A program consists of a series of statements separated by
   a newline character. *)
program = { statement, new_line } ;

(* This should represent all statements currently supported by
   the simpylic parser. *)
statement = return_statement
    | if_statement
    | while_statement
    | expression ;

(* This should represent all expressions currently supported by
   the simplylic parser. *)
expression = number
    | identifier, "=", expression
    | ( unary_operator, expression )
    | ( expression, binary_operator, expression )
    | "(", expression, ")" ;

return_statement = "return", white_space, expression ;

if_statement = "if", expression, ":", ( statement )*
        ( "elif", expression, ":", ( statement )* )*
        [ "else", ":", ( statement )* ]

while_statement = "while", expression, ":", ( statement )*

unary_operator = "!" | "~" | "-" ;
binary_operator = "+" | "-" | "*" | "/" | "and" | "or" | "==" | "!=" | "<" | "<=" | ">" | ">="

```
