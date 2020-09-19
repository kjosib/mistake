Report on the *Mistake* subsystem
======================================

Why this project?
--------------------

I began work on this project (in mid-2020) because I thought something like it was missing from
the programming ecosystem. Rather, there are bits and pieces of these ideas implemented hither
and yon, but I didn't see a complete package that combines the entire set of ideas.

I had been doing a lot of dead-simple financial reporting in Python out of a combination of relational
databases, spreadsheets, and random other files. Each new requirement meant another short program,
anywhere from a few dozen to a few hundred lines, and importing a common library of code to
access the various different data formats. (For practical reasons, not all data could "live"
in the relational database.)

I soon saw that the text of these programs was rigidly formulaic. The only real parameters
were: what source data, how to slice and dice it, and how to present it for output. But each part was
deeply intertwined with the others: touch one thing and seven other places required a careful update.
The obvious consequence was an uncomfortable level of caution bordering on fear any time
something about requirements or source data changed.

The real problem was that these programs were algorithmic in nature. But of course they were!
Python is an algorithmic programming language. To get stuff done in Python, you provide an
operational statement about how to accomplish a particular task. What you do *not* do in Python
is provide a collection of generalities and requirements, expecting the computer to work out
the particulars and check that it all makes sense *a-priori*. But this became my general desire.

Thus, some ideas began to percolate. I wanted another programming sub-system that would
interoperate with (regular) Python, but have a completely different set of
semantics for its expressions. That means one part DSL, one part API.


Desiderata:
---------------

* Relationships rather than algorithms.
	It's a truism in software that if you have the data structures and semantics, then the algorithms
	are self-evident, but the reverse is false. (This fact is central to my initial motivation.)

* Deal with collections rather than individual elements.
	"Collections" should include *at least* homogeneous tensor-like objects, but some others are planned.
	A consequence is that the DSL has no overt expression of looping behavior.
	(Operational behavior is implied and handled behind the scenes.)

* Check yourself *before* you wreck yourself.
	Semantic validation should happen up front, before loading any application data.
	This can be seen as type-checking, where the type system extends
	to the shapes of, and the units-of-measure for, expressions in the language.

* Do everything by name rather than positional sequence.
	Is the data indexed internally by region and then product, or by product and then region?
	Curse that! It should not be the programmer's problem. Let the computer keep track.

* Do nothing until it is (apparently) necessary.
	The subsystem should read and compute only what it must in order to answer a query.
	The DSL is thus "lazy" rather than "eager".

Lessons Learned:
----------------------------

The rest of this document will slowly expand to cover lessons learned as they become evident and I have time.

