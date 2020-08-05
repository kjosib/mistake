# Keep it Simple, Simon!

(People are *NOT* stupid. Don't call them that. They do, however,
have limits, and we should respect that.)

This tickler-file lists deliberate oversimplifications
that currently exist in the code base and/or general design.
By writing them down somewhere I hope they will be neither
forgotten not nitpicked.

----

Wherever some detailed semantic structure has yet to be defined,
I'll just expect `id` in the grammar. Anyway, it's going to work
out that you can define and name virtually any interesting sort
of object, so this is almost always a correct decision.

----

Early on, the language defined in the grammar need not reflect
any presumed supporting structures. Experimentation requires
flexibility.

----

For now, "dimensions" are just names, and the only function is
to compute dimension-judgements. That means I only need a way
to define cubes (spaces?) and have one or two naive "operations"
upon such values. I can make it better LATER.
