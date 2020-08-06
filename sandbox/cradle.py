r"""
{-
Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.
-}

this_is_an_identifier where foo < 1_000 else bar -- This is an end-of-line comment.

"""

from mistake import frontend

import toys

parser = frontend.CoreDriver(frontend.TABLES)
ast = parser.parse(__doc__)
print(ast)
