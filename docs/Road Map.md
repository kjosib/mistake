# Road Map:

## General Plan of Attack:

The compiler needs to be primed with a definition of the application environment:
these are the "built-in" objects as far as the script is concerned.

* Define Environment (API calls)
* Parse Script Text into AST
* Walk AST with environment in mind to build a semantic model (what kind?)
* Judge types and plan queries ("Perform Miracle")
* Return a "script" object (which basically is a bunch of query plans)

The "script" object implements API methods for getting data streams (magically?)
by name based on the instructions within the source text of the script. At that
time, methods registered with the environment may be called by-need.

Some sort of sample application should use CSV files as a data source.
A second sample should show how to use a collection of CSV files and
load data at-need. This MEANS something: The run-time API must be able
to ask the application environment for a particular slice of data.
However, it should not be too demanding: A data source object might not
be fit to perform every sort of slicing, so it will need to tell the
API just exactly what kind of slicing it's organized as -- perhaps by
way of a "data catalog" mechanism.

It may be worthwhile to provide a utility library with a few simple tricks
and nonsense over CSV files so that
1. client-applications don't need to invent the wheel, and
2. It provides a nice sample basis for doing fancier, smarter things with SQL.

## Bits that work, at least in some form:

* Simple type-judgements, including a text representation thereof.
* Simple equations are translated to simple query-steps.
* Query steps follow something of an interpreter-pattern.

## Bits yet to implement:

* Registry of environmental scalars
* Pluggable API for query predicates

## Bits I'm not sure about:
* Maybe named predicates?

From there, the rest should be mostly downhill. I do anticipate a speed-bump
with data-catalogs, but not too bad with evolutionary development.
