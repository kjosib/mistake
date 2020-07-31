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

A language is more than syntax: it's a coherent set of semantics. These can be
so arranged that the structure and constraints on data are expressed once (together)
and the essential ideas about *using* the data are not cluttered up with
holographic echoes of the structure.

By tying the DSL back to Python in key places, it's easy (I hope) to bolt this
into an existing pipeline. Ideally you'll write *Python* where *Python*  makes
the most sense, and write *Mistake* code where *Mistake* makes the most sense.

## Where do we stand?

Nothing. It's conceptual at the moment. I do have some ideas how to proceed.
The grammar file at `src/mistake/mistake_grammar.md` will slowly grow a
plain-language description of the semantics.

Additionally, the `docs` folder contains design considerations.
