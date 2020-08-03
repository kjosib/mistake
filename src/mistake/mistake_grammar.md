# Grammar Definition for "Mistake" Language

Let's begin with a few fairly-standard lexeme definitions:

# Definitions

```

```


# Patterns INITIAL


```
\{- :enter BLOCK_COMMENT
\s+ :ignore whitespace
--.* :ignore eol_comment
\l\w* :word

```

# Patterns BLOCK_COMMENT

```
-} :enter INITIAL
[^\-]+ |
-+/[^}] :ignore comment

```

# Productions

```

start -> ID

```

