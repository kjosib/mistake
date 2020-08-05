# Grammar Definition for "Mistake" Language

Let's begin with a few fairly-standard lexeme definitions:

## Definitions

```
digits \d(_?\d)*
```


## Patterns INITIAL


```
\s+   :ignore whitespace
--.*  :ignore eol_comment
\{-   :enter BLOCK_COMMENT

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
%void where else
```

## Productions
Keeping it super-simple for now: just a few parse rules to
get something going. I'm going with upper-case non-terminals
and lower-case terminals this time, to see how I like the look.
```
TENSOR_EXPRESSION -> id
    | id where PREDICATE else id

PREDICATE -> id relop SCALAR

SCALAR -> integer
SCALAR -> real

```

