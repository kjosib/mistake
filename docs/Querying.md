# Querying and Predicates

The little language so far describes abstract relationships between data sets.
The question becomes how to represent queries.

One idea is that you have a section which describes the schema (and which can be shared widely)
and then another section which cuts things down according to the concrete question you're asking.

Anyway, let's suppose you want to know the European sales for a certain product line.
Assume you have a plug-in tensor `sales` that gives sales by country and
product, and a defined aggregation for regional sales by product line
called `rpl`.

You are basically asking the system for that section of `rpl` where the
product line is `$FOO` and the region is `Europe`, and it's best if
the system does the minimum necessary work to get that answer.

Now, one method is to compute the entire `rpl` tensor and then filter.
But this is wasteful if our sales figures are already indexed -- say,
by country. For example, you might have separate files by country.

Let our `.stream(...)` method accept a `Predicate` object of some description.
In this case, the predicate constrains both region and product line.

The `[country] -> [region]` aggregation node ought to translate
the `[region]=Europe` predicate into `[country] satisfies predicate $P`.
A similar story applies to `[product] -> [line]`.
Then, the `sales` tensor gets this new-and-improved predicate.

But how to deal with it?

The `sales` tensor clearly needs to be able to process the `[country]`
predicate. Now, MAYBE `[country]` has a further index on `[region]`,
in which case we can consult the index (this is a question of implementing
the `country` dimension?) and MAYBE we need to perform a `[country]`
table-scan, but AT LEAST `sales` should be able to ask for an iterator
of satisfactory `[country]` (because that's how `sales` is indexed) and
then to furthermore rely on the remainder of the query-predicate for
all further (say, product-level) filtration.

I'm considering that a predicate could be defined which takes
two or more dimensions as input. Yet, data might be indexed along
zero or more of these dimensions. So, in general, the manipulations
on predicates are:

* Leave it for the basis tensor to deal with.
* Replace one criteria-space with another.
* Iterate the desired fraction of an index-space.
    * This only makes sense for small closed finite spaces.
    * Maybe we leave this to plug-in authors to respect?
* Test a (partially-specified) point for (possible) membership.
* Divide into two (or more) predicates -- e.g. one for index operations
  and one for table-scanning operations.

What about the API? Let's don't overburden plug-in authors!

## Keep it Simple, Sally!

A CSV-file plug-in will look and act rather differently from a SQL-backed
plug-in. Both need to be able to do the right thing regardless of what
predicate might come in.

For the initial API, the plug-in can be responsible for respecting
the entire predicate. Later experience may suggest convenient short-cuts.

At this moment, then: what seems to make the most sense is to let the
query API rely on named parameters bound to a particular dimension by
their use in predicates.

## Some implications:

The (exported) query API should probably expect the name of a tensor
and a dictionary of relevant parameters. These can be tested for
adequacy and sensibility before running the query because each tensor
depends on some subset of known parameters.

In the context of Python as host-language, it may be nicely idiomatic
to offer (perhaps only) a context-manager interface for setting query
parameters. This would make extra sense in applications that query
several tensors for one coherent interaction with the end-user.

I expect that in a sizable application, it may be tempting to want to
provide additional dimensional constraints at the query boundary.
I haven't decided yet if that's wise, so I'll skip it for now.
