# Musings on the design

This file is a temporary holding pen for ideas that don't yet have a better home.

## Query Planning

So this is about the time I begin to figure the validator could also plan queries.
Simply put: instead of returning only the type of an expression, it could return
an object consisting of both type and plan. In case of a mis-typed expression, the
"plan" would be to raise an exception. This could result in a system where even
if parts of a domain model are ill-typed, the well-typed parts can still function.
That may have considerable practical value.

## Proper Automatic Testing

Most of the juicy bits are about the system catching broken expressions.
Since the validator object takes a "complain" function as a parameter,
it's well-suited to unit-testing: just pass it a function that tells
the test suite (not the end user) what's going on. That'll be coming.

A "space assertion" provides a way to check the validator's work for
the portion of tests where it *is* expected to succeed.

## Proper Documentation

It will soon be time to spin up another Sphinx.
Sections should include tutorials, examples, reference.
Open question: how to organize a tutorial? Also, should there be a tutorial module?
Note also this is an embedding language, so it need an application context.

## Profiling and Performance Tuning

Eventually someone is going to be concerned with performance. Most times,
we make this kind of a system run faster by making it perform less work.
I anticipate there will be some sort of "Tensor Service" interface
that deals in standardized query parameters. There are a few basic ways
this goes wrong:

* Selecting too much data (thus wasting effort)
* Selecting not enough data (and having to make multiple round-trips)
* Forgetting too soon about data recently selected (repeating work)
* Expecting the tensor service to be too smart (a maintenance hell)

The balance is tricky. If a given "Tensor Service" can strongly benefit
from one or two specific query parameters, it should negotiate that with
the query planner. This aspect strongly resembles the wise selection of
indexes in a SQL database.

As for actual performance *measurement*, the generic profiling module
is a good start for understanding which services run slow. However,
it may also be worth looking specifically at how much data gets selected
and subsequently either filtered out or summarized, because both represent
opportunities: either to push a filter upstream, or to cache a summary.

Relating to the last point, whenever a client application requires some
computation, it's best to ask for all the things you want in one transaction,
because it will presumably allow the query planner to do its best work.

## REPL:

I think I want a REPL for ad-hoc queries, similar to a SQL console.
This suggests a simple REPL should be an ordinary method-call away,
because most of the good stuff relies on whatever application-defined
data access methods. Think of it as an interpreter with a standard prologue.
Maybe it should use `readline` out of the box. Maybe a simple tkinter version
should also be provided. And this suggests another channel of environmental
interaction to present results after the fashion of an APL environment.
So automatically there's call for a presentation of data grids.

But the system should also be scriptable for batch-process jobs.

At any rate, some of the console output stuff is great for debugging.

As an aside, a REPL should probably not create symbol table entries for broken definitions,
and it should also probably allow to reset (or maybe commit?) a vocabulary so far.


## Curves:

Along a time axis, these can be integrals or derivatives.
Derivatives are a sequence of increments. Integrals are a sequence of replacement values.
Either kind of curve can possibly have a particular value in the "beginning of time" position.
Absent such a value, the curve is considered to be all-zero before the first proper sample.

Thus, "beginning-of-time" (BOT) is a special distinguished kind of time ordinal which works like
negative-infinity. Corresponding to positive-infinity is "end-of-time" (EOT) which doubtless
adds clarity in various circumstances, but one should probably not have actual samples at EOT.

## Axis Types:

Time:

You can have regular intervals, or you can have arbitrary intermittent intervals.
You can also incidentally have more than one time dimension for various reasons.
Also, intervals have a certain hierarchy and you should be able to perform reasonable
grouping and slicing along that hierarchy. 

Array:

In this case you have a smallish pre-defined set of ordinals which have some established
(if arbitrary) ordering. These ordinals may also have attributes and even participate in
containment relationships with other (presumably smaller) roll-up arrays.

List:

An arbitrarily-long (data-driven) sequence of unique identifiers: a definition must provide
the natural ordering and attributes for these.

Record:

An ordered collection of ordinals each of which is also associated with some deeper structure.
Individual fields may be operated on independently.

## Storage Classes

No references to internal storage organization should be necessary in the surface syntax. 
However, there could be lots of different ways in which data get stored and retrieved, as
well as held in memory. So long as the objects in the environment play nicely with the API,
then all should be well. That said, it may be worthwhile to offer a few knobs.

## "Sticky" Dimensions

Say you've sliced out a sample from a curve corresponding to the measure on January 5th.
That sample should probably remember the fact that it was relevant to January 5th.
So later on, if you try to add it to another sample (taken from January 6th) then the time
dimension may be consulted to see if this is a good idea.

Actually, you wouldn't make the check at run-time, but would do it during the analysis phase.
We don't have to know the specific dates; just whether adding samples arbitrarily like this
even makes sense. (Hint: it probably doesn't unless you're performing a defined grouping
operation which the time dimension may provide for.)

More generally, we can track where our numbers came from to make sure we are operating on
them in sensible ways.
