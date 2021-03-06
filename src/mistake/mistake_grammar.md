# Grammar Definition for "Mistake" Language

Let's begin with a few fairly-standard lexeme definitions:

## Definitions

```
digits       \d(_?\d)*
identifier   \l\w*
```


## Patterns INITIAL

```
\h+          :ignore whitespace
(--.*)?\R    :token newline
\{-          :enter BLOCK_COMMENT

{identifier}    :word
\${identifier}  :sigil env_scalar
@{identifier}   :sigil env_list
&{identifier}   :sigil named_predicate

<        :relop LT
<=       :relop LE
==?      :relop EQ
<>|!=    :relop NE
>=       :relop GE
>        :relop GT

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
%void else week space tensor of is newline sum
%void means not in
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
    | _ where CRITERION   :filter
    | _ where CRITERION else _  :multiplex
    | _ sum '{' SSL(MAPPING) '}'  :sum_image
    | _ sum '{' SSL(MAPPING) '}' by SPACE  :sum_image_onto


FACTOR -> id | '(' TENSOR_EXPRESSION ')'

CRITERION -> id relop SCALAR    :criterion_relative
CRITERION -> id in SET          :criterion_within
CRITERION -> id not in SET      :criterion_without

SCALAR -> integer | real | string | env_scalar

SET -> env_list
     | '{' CSL(SCALAR) '}'        :enumeration
     | '(' SCALAR ',' SCALAR ')'  :open_interval
     | '(' SCALAR ',' SCALAR ']'  :open_closed_interval
     | '[' SCALAR ',' SCALAR ']'  :closed_interval
     | '[' SCALAR ',' SCALAR ')'  :closed_open_interval

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

