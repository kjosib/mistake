Introduction
===============

Some sizable amount of programming problems boil down to gnashing tensor-like
data together in various ways. A good RDBMS can handle some of this for you,
but even SQL has its limits. Furthermore, it's not always desirable or feasible
to keep absolutely every fact and function in the relational database.

If:

* You have a few dozen megabytes of mainly-numeric data (keyed in various ways);
* You frequently and very carefully slice, dice, chop, mince, julienne, blend, and puree your data;
* SQL *by itself* is insufficiently flexible, expressive, concise, or complete for your querying habits; and
* You are sick and tired of writing *almost, but not quite exactly,* the same subroutines over and over;

then perhaps this package is for you.

*Mistake* is a multifaceted data-processing subsystem with a focus
on semantic validation, flexibility, and programmer velocity.
It is meant to complement your existing relational and other data stores,
not replace them.

*Mistake* is not yet a mature system. Indeed, at the time of this writing
it's only barely functional for toy projects. However, it's time to start
on some documentation.

*Mistake* has several major parts working together. These include:

* A domain-specific language provides syntax and semantics particularly suited to selecting and massaging tensor-like data.
* Shape analysis checks that your data has appropriate indexing structure for the operations to which it may be subjected.
* Dimensional analysis checks your arithmetic for meaningful units of measure.
* The data-source API enables you to connect arbitrary data formats and files.
  It includes provision to load only what's necessary based on the actual parameters to a query.
* The client API provides for invoking queries (with bound parameters) and using the results in convenient ways.

