# Units of Measure

I'd like this system to respect dimensional analysis. Trouble is, any given
application domain should have its own set of relevant units of measure.

* A graphical application might be concerned with pixels, inches, etc.
  You may or may not wish to distinguish horizontal from vertical pixels.
 
* A financial model may track money, widgets, prices, discount rates, etc.
  It may or may not worry about different currencies.

* A physical model may worry about distance, time, mass, temperature, current,
  luminance, particle-count, and grant funding. It probably includes a conversion
  factor from money to CPU cycles.

## Problems with the ordinary model

The most common way to think about dimensional analysis is to keep track
of the exponents on (fundamental) units. However, this misses a few key ideas.
For example:

* Work and torque both have the same units (force * distance) but they
  mean very different things and should not be conflated.

* Reynolds number and a percent-off discount coupon are both dimensionless
  ratios, but again they have completely different semantics.

Additionally, the usual model fails to distinguish between points and vectors:

* An object's current position is its initial position plus the sum of
all its incremental displacements over time. But you cannot reasonably add
the positions of two objects. (You might think to average their position.
Think instead to find a point at half the offset from one to the other.)

* You can add a month to July 4th, 1776, but you cannot meaningfully add
two dates together. The algebra should distinguish dates from intervals
and do the right thing regarding differences.

What can be done?

## Tactic 1: Specialized Fundamental Quantities

For the work-vs-torque problem, we need to distinguish between force
tangential to a lever arm, and force exerted on an object parallel to
its motion through some distance. One idea is to distinguish three kinds
of fundamental distance: translation, tangential, and radial. Thus,
rotation would simply be tangential (circumferential) distance divided
by radial distance (and thus neither "dimensionless" nor fundamental).
Working that way, torque has *completely* different units from work.

## Tactic 2: Richer "Dimensionless" Ratios

For Reynolds number vs discount, observe that you only ever discount
money (or things with money in the numerator). Contrariwise, fluid dynamics
equations should not be in the same paragraph as money. Supposing we think
of discounts as *dollars per dollar*, then naturally we can only multiply
(or divide?!) them by some other quantity involving dollars.

By the way, a discount is not about dollars per-se, but about money as a
fundamental quantity. Unfortunately modelling that fact is beyond the
current scope of this endeavor. (Perhaps later I may attempt it.)

You could also choose to model a separate categorical unit of money just
for discounts (as in tactic #1) but that gets really weird really fast.

Scalar fractions appear in many applications. You may say, for instance,
that earned value is proportional to completed progress. Then in principle
this says that a progress ratio may be multiplied by a price. We can
model this idea by declaring the ratio not to have any particular
required unit (or quantity) to which it is applied.

Suppose you want to solve problems with Reynolds numbers (such as inferring
needed pipe diameters to assure laminar flow). You know in advance that
some combination of physical quantities are even remotely relevant; others
are probably not.

## Tactic 3: Absolute and Relative Unit Dualities

We can say that `Date(...)` objects are absolute, where as `TimeInterval(...)`
objects are relative, and they are each other's dual.

The relative units form an additive ring, so they don't need any special
annotations. Absolute units cannot be added, multiplied, or divided with
directly with each other, but their difference yields their dual, which
may be added back.

To implement this idea in code, a unit definition will have an optional
field naming the *dual* unit. If this field is non-null, then the
appropriate arithmetic semantics should be enforced.

## How to enforce sanity, then?

In principle there's nothing to stop you from writing an expression
for dollar-word-amp-seconds per square kilogram-meter-candela, but
I cannot imagine an application in which such a unit even makes sense.

The semantic framework automatically means you cannot accidentally
add (or subtract) incompatible quantities: it would be detected at
compile time.

It may be possible to draw a box around sanity by means of "laws"
similar to the Ideal Gas Law. If you know that `pv=nRt`, then you
also know that the associated quantities (and units) may reasonably
participate in the associated arithmetic.
(You also have a dozen different implied formulas, but I digress.)

A factory might care about widgets per hour, or dollars per widget,
but probably look askance at anything involving widgets squared.

A "gradual manifest typing" approach would say that we declare,
for our choice of expressions, the units we think they should have.
(If there's ambiguity, require the hint.) The system verifies
that the declared units match the calculated units, or else complains.

One final shortcut is to declare that, in the absence of a hint,
a final-result tensor must have one of X, Y, or Z units. Then if
someone tries to query an un-hinted tensor with some other unit,
the runtime should complain that its units are wrong for export.

## What about conversion factors?

Feet. Inches. Meters. If you have a standard unit for the fundamental
physical quantity of length/distance, then the other units naturally
host a conversion factor.

It may be reasonable to combine the application of these factors
with the syntax that provides unit-hints. Thus, if your value is
said to be "in inches" it clearly must be length (or just wrong).

