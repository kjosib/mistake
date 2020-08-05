# Bestiary

A [bestiary](https://en.wikipedia.org/wiki/Bestiary) is a compendium of beasts.
Originating in the ancient world, bestiaries were made popular in
the Middle Ages in illustrated volumes that described various animals and even rocks.
The natural history and illustration of each beast was usually accompanied by a moral lesson.


The beasts in *this* catalogue are the names, shapes, and characteristics of fundamental
operations and objects in the language to be discovered.

## Data and its Semantics

**Scalar:** Real numbers, dates, times, intervals, as well
as `BOT` and `EOT` for beginning and end of time, respectively, may find
particular use in program text.

**Opaque:** Parameters from the environment may be available by name only,
for reference in formulas.

**Tensor:** A collection of scalar (generally real-valued) data corresponding to each
point in the cross-product of one or more dimensions. Every tensor has a shape,
described next.

**Shape:** A collection of distinctly-named dimension instances
(along with any semantic parameters)
which describes the semantic
organization of some tensors that may be processed. Shapes are much like types
in conventional programming languages, but they've a richer semantics. They
have structural equivalence rather than name-based equivalence.

**Dimension:** A description of a set of possible (or reasonable) ordinals,
along with formal-parameters.
These have name-based equivalence.
Much of this ties back to the application integration layer.

## Kinds of Dimensions

**Sequence:** The ordinals represent consecutive intervals in a clear linear progression.
They can generally be grouped in a hierarchy from smaller to larger units
without overlap. Since the ordinals are totally-ordered, then the usual
six relational operators work in the usual way.
*Instances* of time-like dimensions may be incremental or cumulative, which
influences what kinds of operations are reasonable. In particular, it makes
sense to sum over increments for grouping.

**List:** The ordinals are arbitrary members of a set without defined successors,
intervals, or *natural* order (although some incidental ordering must inevitably
be imposed on output: often alphabetical, but sometimes taken from a pre-defined list).
Lists are collapsible: you can sum over them. They may have any set of
direct and indirect attributes which (a) may be referenced for hierarchy-like
groupings, and (b) must be
defined via the integration layer. In particular, boolean predicates will
be identified in the syntax with `?` and their negation as `~?`.
A list-type dimension can also have "natural subordination" to some other dimension,
in the sense that its ordinals only make sense within the context provided by
that other dimension. In such case, you cannot have this dimension without also that one.

**Record:** A set of fields with pre-defined arbitrary well-known distinct
identifiers and no *natural* ordering. Individual fields may have
heterogeneous subordinate shapes. (*Instances* of record-type dimensions
may collapse some of these, though.)

In general *record* types can be profitably described using the language directly.
Records are not inherently collapsible, but instead sensible mathematical relationships
are defined (as part of the record definition, not all over creation) and these may
be used wherever a field might instead be given directly.

## Operations on One Structure

**Indexing:** Given a dimension and ordinal, you can pull out a sub-tensor of
one rank smaller. The result will carry forward the association though.

For cumulative dimensions, you generally want the attested index no less than,
(or no greater than, or etc) the actual parameter. Suitable syntax for this
kind of "approaching" idea must be provided.

**Projection:** This is the generic name for taking one dimension to another.
(In the deeper abstract, you might reasonably project from any set-of-dimensions
to any OTHER set-of-dimensions, but that's very rare and can be put off or done
differently.) Anyway, the operation fundamentally
needs a source dim, a target dim, and an aggregate function. About 95+% of cases,
that aggregate is mere summation. Most of the rest can probably be done with
`convolve` and simple arithmetic. The rare exceptions might call for a plug-in.

**Grouping:** Since the relationships between dimensions and attributes are
known in advance, these can all be checked and planned before data-intensive
or compute-intensive activities. This is a special case of projection in which
the environment provides a function from one dimension to another, and the
relevant aggregate-function is summation.

**Convolution:** This is your simple arithmetic between fields of a record.
Ideally these can be defined simply with a set of formulas assigning to the
new fields in terms of the old fields. Operationally, it might be done in
two phases: one organizing the data so that all corresponding inputs are
together (on the same "row", as it were); the second evaluating the formulas
for each "row". To the extent analysis can push that organization back the
data supply chain, analysis wins.

**Slicing, etc:** I see this being a component part of larger coherent operations.

**Inspection**: To help see what's going on, show the judged shape of some expression
and exit(9) after all such inspections have been performed. Or something?

**Running Sum and Pairwise Difference:** How you convert incremental to
cumulative and the reverse. NB: one of these operations followed by window
slicing the same dimension is an opportunity for query optimization.

## Operations Between Scalars and Structures

The usual "element-wise" rules apply.

## Simple Operations on Two Structures

`a + b` : `a` and `b` have the same shape and are not cumulative in any dimension.
Adds element-wise. Un-paired elements retain their original value.

`a - b` : Equivalent to `a + (0-b)`.

## Parameterized Operations on Two Structures

**Multiplexing:**
`a where x<=y else b` : `a` and `b` have the same shape including dimension `x`.
Result has again the same shape, with elements drawn from `a` which DO satisfy the
predicate `x<=y` and also those drawn from `b` which do *not* satisfy the same predicate.
The predicate must be applicable to the dimension.

## Integration Points


### Tied Tensors

How shall we get data from the world into the language?
Answer: Register constants and implementations for demand-loading application data.


