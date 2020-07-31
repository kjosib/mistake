# Theoretical Underpinnings:

## Mathematical Ideas

Most people are familiar with the progression from scalar to vector and then matrix.
Collectively, these (along with higher-dimensional analogues) are known as tensors.
The number of dimensions of a tensor is called its "rank", so a matrix is a rank-2
tensor. To describe the size of a tensor, we list the sizes along each of its dimensions:
the size of a tensor is therefore a vector, except that the size of a vector is a scalar
and the size of a scalar is one.

Operations can be defined over and between tensors, including those of different rank
or size. A few are commonly described in books on linear algebra. Several more can
be found in writings about APL. The vast majority shall have to be defined at need.
There will, no doubt, be some common idioms. These can be discovered. At any rate,
some unfamiliar notation will be necessary.

## Everything is a Tensor (or is it?)

No, not exactly, but tensors are pretty common if you squint. A lot of applications
in business and scientific data can be seen as mashing around tensors in various ways. 

The relationships between tensors drive much complexity in data processing
applications. These relationships are fundamental to a problem domain; their
influence echos throughout our programs even without any central expression.
A suitable notation must express these relationships overtly so that sensible
things are easy and nonsense can be detected during semantic validation.

## Human Factors (or, Essence and Accident)

In a typical general-purpose programming language there is no clear conceptual
expression of the relationships that inform design and algorithm. You get mired in
clerical details and inevitable arbitrary choices while remaining free to compare
apples and oranges.

I wish a notation and corresponding semantics expressly designed for cleaning up
that mess, automating the incidental minutia, and staying out of conceptual trouble.

### Associative Indexing

That number in the third column of the seventh row: What is it the measure of?
Questions like this are why the axes of a tensor should have index labels.
I don't care to keep track of which-numbered row and column; only that I
want the `population` of `India` in `2007`.

Accordingly, axes have type according to the set of admissible ordinals.
They might be:

* drawn from a finite or infinite set
* have natural or arbitrary ordering
* be considered as numbers, dates, strings, etc. 

### Axis Names
A related deficit is that "tensor" axes ought to be named rather than
numbered: we talk of rows and columns (or worse: axis 0, 1, 2, 3, 4) which,
being universal and homogenous, are easy to confuse in nontrivial
applications. A series of stock prices should have dimensions of time,
ticker symbol, and maybe a record/field structure of "open,high,low,close".
Nobody particularly should care about these being respectively rows, columns,
or planes -- except when it comes time to store and retrieve data externally.

There are plenty of "array-oriented" high-level programming languages, but the
ones I've played with all suffer this same essential misfeature of ordering
rather than naming the axes.

So data can't avoid having some sort of physical organization, but most of the
time I don't want to be bothered about what that organization happens to be.
Let the computer just pick something and keep track for me.

### Element-wise Operations, Ontology, and Dimensional Analysis

What do you get when you multiply a matrix by two? You get a new matrix in which
each element is twice the element in the corresponding position of the original
matrix. The same idea holds for tensors of all ranks multiplied by a scalar.

What about a matrix multiplied by a vector? We should do it like APL -- except
that instead of having a row- or column- vector, we instead require the vector
declare which (named) axis it's along in some grand universe of discourse.

With that in mind, if this particular axis allows multiplying, we can multiply.

More generally, we can specify up front that certain kinds of operations
between specific groups of dimensions *make sense* in our ontology (along
with the dimension of the result), and then the entire program is constrained
in a way that a typical language just cannot provide.

* Example: it generally makes no sense to sum up the open and close price
of a share of some stock, but perhaps their average or difference has meaning
in your problem domain.

### Records, Arrays, and Subspaces

## Limitations of the Theory

Not everything in the program should be crammed into tensor logic. Practicalities
of input and output (e.g. loading data on-demand from different sources) and
complex business logic should all be delegated to the 3GL (in this case Python).
Thus, there must be a suitable interface for application-specific plug-ins.

With that in mind, a few handy bits in the library for dealing with common
cases might be well-received.
