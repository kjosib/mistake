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

## Bits I am *currently* working on:

Slated for the next release:

* Asymmetric Tensor Arithmetic operations: `o<` and `o>` for `o` in [`*+/-`].
* Automated tests for the semantics module.

## Bits that work, at least in some form:

* Simple type-judgements, including a text representation thereof.
* Simple equations are translated to simple query-steps.
* Query steps follow something of an interpreter-pattern.
* Query Input Variables (both scalar and list, with perl-style sigils)
  although in principle the distinction could be done purely by context


## Bits for which there is grammar but no further support:

* Interval and set expressions for criteria

## Bits with lexemes but no grammar:
* Named predicates: The idea is these have some sort of input-space
  and you can either supply a Python plug-in or declare them inline.

## Bits yet to implement:

* More operations on the internal notion of a "dimension":
  * validating scalars.
  * validating ranges/intervals/sets. (Intervals only when the dimension has a natural order.)
  * validating order-type relops that there must be a natural order. (or provided collation?)
* Compare the argument and the relation to the type of the dimension.
  * I've forgotten what this means.
* Pluggable API for query predicates
  * Maybe a couple different API levels for more or less sophisticated plug-ins?
* Filter on predicates derived from mappings
  * that is to say, apply a map and a filter without changing the "space"?
* Syntax for trivial "get-attribute" mappings,
  along with appropriate de-sugaring
* Natural syntax for predicate composition
  * Does this require more sophistication from a plug-in?
* Rasterized Curves (these must know various extra bits)
* Incremental vs. Cumulative Rasters.
* Appropriate "promotion" strategy for mixing rasterized
  and sparse expressions.
  * Thus, plug-ins must report as raster-oriented or not.
* Some sort of simple (interactive?) outputs.

## Bits I'm not sure about:

From there, the rest should be mostly downhill. I do anticipate a speed-bump
with data-catalogs, but not too bad with evolutionary development.
