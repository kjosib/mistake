r"""
{-
Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.
-}

this_is_an_identifier -- This is an end-of-line comment.

"""

from mistake import frontend

frontend.CoreDriver(frontend.TABLES).parse(__doc__)

