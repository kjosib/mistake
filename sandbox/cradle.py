r"""

Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.

"""

from mistake import frontend

frontend.CoreDriver(frontend.TABLES).parse("this_is_an_identifier123")

