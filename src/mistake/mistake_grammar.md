# Grammar Definition for "Mistake" Language

Let's begin with a few fairly-standard lexeme definitions:

## Definitions

```
digits \d(_?\d)*
```


## Patterns INITIAL

```
\h+   :ignore whitespace
(--.*)?\R    :token newline
\{-   :enter BLOCK_COMMENT

\l\w* :word

<     :relop LT
<=    :relop LE
==?   :relop EQ
<>|!=    :relop NE
>=    :relop GE
>     :relop GT

{digits}            :integer
{digits}\.{digits}  :real

'.*'    |
".*"    :string

->         |
{punct}    :punctuation

```

## Patterns BLOCK_COMMENT

```
-} :enter INITIAL
[^\-]+ |
-+/[^}] :ignore comment

```

## Declarations

```
%void where else week space tensor of is newline sum
%void '(' ')' '[' ']' '{' '}'
%void ',' ';'

%left '*' '/'
%left '+' '-'
%nonassoc where sum

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
    | FACTOR by SPACE     :aggregate_by
    | _ '*' SCALAR        :scale_by
    | _ '/' SCALAR        :scale_divide
    | _ '*' _             :product
    | _ '/' _             :quotient
    | _ '-' _             :difference
    | _ '+' _             :tensor_sum
    | _ where PREDICATE   :filter
    | _ where PREDICATE else _  :multiplex
    | _ sum '{' SSL(MAPPING) '}'  :sum_image
    | _ sum '{' SSL(MAPPING) '}' by SPACE  :sum_image_onto


FACTOR -> id | '(' TENSOR_EXPRESSION ')'

PREDICATE -> id relop SCALAR    :criterion

SCALAR -> integer | real | string

SPACE -> '[' NCSL(id) ']'

MAPPING -> DOMAIN '->' DOMAIN :mapping

DOMAIN -> id :one | SPACE

```

Need a few macros then:
* `CSL` stands for "comma-separated list of (one or more)"
* `NCSL` stands for "comma-separated list of (zero or more)"
* `SSL` stands for "semicolon-separated list of (one or more)"
```
CSL(x) -> x :one | _ ',' x :more
NCSL(x) -> :empty | CSL(x)
SSL(x) -> x :one | _ ';' x :more

```

