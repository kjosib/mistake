# Musings on the design

This file is a temporary holding pen for ideas that don't yet have a better home.

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
