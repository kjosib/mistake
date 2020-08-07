# Grammar Definition for "Mistake" Language

Let's begin with a few fairly-standard lexeme definitions:

## Definitions

```
digits \d(_?\d)*
```


## Patterns INITIAL


```
\R    :token newline
\h+   :ignore whitespace
--.*  :ignore eol_comment
\{-   :enter BLOCK_COMMENT

{punct}    :punctuation

\l\w* :word

<     :relop LT
<=    :relop LE
==    :relop EQ
!=    :relop NE
>=    :relop GE
>     :relop GT

{digits}            :integer
{digits}\.{digits}  :real

```

## Patterns BLOCK_COMMENT

```
-} :enter INITIAL
[^\-]+ |
-+/[^}] :ignore comment

```

## Declarations

```
%void else week where space tensor of is newline
%void '(' ')'

%left '*' '/'
%left '+' '-'
%nonassoc where

```

## Productions START
Keeping it super-simple for now: just a few parse rules to
get something going. I'm going with upper-case non-terminals
and lower-case terminals this time, to see how I like the look.

```
START -> STATEMENT :first
    | _ newline STATEMENT :subsequent

STATEMENT -> :empty_statement
    | id is TENSOR_EXPRESSION  :define_tensor

TENSOR_EXPRESSION -> FACTOR
    | _ where PREDICATE else _  :overlay
    | _ '-' _     :difference
    | _ '+' _     :sum

FACTOR -> id
    | _ '*' SCALAR :scale_by
    | '(' TENSOR_EXPRESSION ')'

PREDICATE -> id relop SCALAR

SCALAR -> integer | real


```

