# Mistake: A tensor-oriented programming language with semantic validation

Some sizable amount of programming problems boil down to gnashing tensors
together in various ways. If you are running simple algorithms over vast
amounts of data, go look at numpy or pandas or tensorflow or...

On the other hand, if you do a lot of interrelated numeric-processing projects
with fiddly requirements for the careful selection and massaging of tensor-like
data on the scale of a few dozen megabytes, then perhaps this package is for you.
(Maybe one day someone will contribute bindings for numpy so we can all grow fat,
dumb, and happy.)

I began work on this language because I think something like it is missing from
the ecosystem. I'd like it to plug into Python because these days everything does,
and I'd like the notation to be sufficiently expressive.

## Why the funny name?

Casting about madly for a project name, I noticed that Edsger Dijkstra called APL
on the carpet as follows:

https://www.cs.utexas.edu/users/EWD/transcriptions/EWD04xx/EWD498.html

    APL is a mistake, carried through to perfection.
    It is the language of the future for the programming
    techniques of the past: it creates a new generation
    of coding bums.

Well, shoot. My whole idea is inspired by APL's array-oriented nature, although
I do take measures to keep things intellectually manageable in ways APL does not.

## Alright then. What's the big idea?

Small to medium-sized data sets, generally numerical, with a great deal of
structure: conventionally the programs to process such data wind up reflecting
that structure *holographically* throughout the code base.

What's more: requirements (or, our understanding of them) change with time.
When your assumptions fall, the ripple effects in a conventionally-written
program are operational in nature: to make the correct changes, you need to
understand how things work at a fairly detailed level.

A language is more than syntax: it's a coherent set of semantics. These can be
so arranged that the structure and constraints on data are expressed once (together)
and the essential ideas *about using* the data are not cluttered up with
holographic echoes of the structure.

Let me amplify that point: In ordinary 3GL programming (and Python is a 3GL) there
is *no verified* part of the program that says how you *should* use data. If two
things are numbers, you *can* add, subtract, multiply, or divide them --
but *does that make any sense?* If we can compute the semantic nature of
expressions in advance of the main bulk of runtime, then we can detect and
prevent semantic errors before they endanger the validity of our computations.

We get some additional benefits from treating the language as a semantic description
of relationships between data and computations. For example:

* Iteration/looping is banished from the syntax. Statements are inherently
  parallel (so you can implement that parallelism any way you like).

* The system can (and should) be "lazy" by only performing that fraction of
  specified computation which is strictly necessary to answer a user's query.

By tying the DSL back to Python in key places, it's easy (I hope) to bolt this
into an existing pipeline. Ideally you'll write *Python* where *Python*  makes
the most sense, and write *Mistake* code where *Mistake* makes the most sense.

## Where do we stand?

Very little. It's still mostly conceptual:

* There is a `sandbox` folder with some embryonic bits that
  are slowly growing into a usable system.
* There is a grammar file at `src/mistake/mistake_grammar.md`.
* The `docs` folder contains design considerations.
* Some modicum of functionality is in the `src/mistake` folder.

The main entry point right now is at `sandbox/cradle.py`. It's currently
focused on developing a simple validation layer. Don't be surprised when
it vomits all over `STDERR`: that is literally its job.

If you want to play with this, it's currently better to
work from a copy of the github version.
