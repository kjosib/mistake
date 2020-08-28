"""
Elements of the runtime are (for now, at least) principally implementations of
AbstractTensor which work by sifting, filtering, and combining other Tensor objects.

Continuing to KEEP IT SIMPLE, SALLY!

Just a note: there's a lot of parallelism between (most of) the structures defined here
and those defined for the front-end parsing AST machinery. At least that's true today.
You might think to just parse directly into these structures. I don't like that approach,
though. I've tried it before (not on this project) and it results in a great deal of
clutter. Part of why is that it's very challenging to keep track of which invariants
apply to an object depending on what phase that object is in. I'm happier to be able
to completely throw away the AST once it's no longer necessary. Objects defined in this
file are a bit closer to the metal. Semantic soundness has already been checked. Etc.
"""
import operator
from typing import Generator, Callable, NamedTuple, Any, Mapping
from .domain import Space, Point, AbstractTensor, Transform, AbstractCriterion, Predicate

class TensorBuffer:
	"""
	I'm making an adjustment: henceforth a TensorBuffer is just an implementation
	detail for other (streaming) tensors. Seen another way, the TensorBuffer is
	involved in things that look more like "reduce", whereas the AbstractTensor
	hierarchy has the "map" role.
	
	For now this bit remains somewhat simplistic.
	"""
	
	def __init__(self, upstream:AbstractTensor, predicate:Predicate, environment:Mapping):
		self.__upstream = upstream
		self.__storage = {}
		self.__schedule = tuple(upstream.space())
		for point, value in self.__upstream.stream(predicate, environment):
			key = self.__key(point)
			self.__storage[key] = self.__storage.get(key, 0) + value

	def __key(self, point:Point) -> tuple:
		""" Find the (hashable) indexing information for the given point """
		return tuple(point[k] for k in self.__schedule)
	
	def get(self, point:Point):
		""" Return the value associated with a given point """
		return self.__storage.get(self.__key(point), 0)
	
	def content(self) -> Generator:
		""" Yield up all the <point, value> pairs in the buffer. """
		for key, value in self.__storage.items():
			yield dict(zip(self.__schedule, key)), value
	

class SumTensor(AbstractTensor):
	""" Simplest possible "work-flow" class """
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
		if hasattr(lhs, 'get') and hasattr(rhs, 'get'):
			self.get = lambda point: lhs.get(point) + rhs.get(point)
	
	def space(self) -> Space: return self.__lhs.space()
	
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		# Note this could possibly yield increments to the same point twice. That's OK because
		# points are incremental -- at least under the assumption that everything else is...
		yield from self.__lhs.stream(predicate, environment)
		yield from self.__rhs.stream(predicate, environment)

def difference(lhs:AbstractTensor, rhs:AbstractTensor):
	return SumTensor(lhs, ScaleTensor(rhs, -1))

class ScaleTensor(AbstractTensor):
	""" This is sort of cheating IN THAT read-through access could be provided if the basis supported it. """
	def __init__(self, basis:AbstractTensor, factor:float):
		self.__basis = basis
		self.__factor = factor
		if hasattr(basis, 'get'):
			self.get = lambda point:basis.get(point) * factor
	
	def space(self) -> Space:
		return self.__basis.space()
	
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		for p, v in self.__basis.stream(predicate, environment):
			yield p, v * self.__factor

class Transformation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space:Space, transform:Transform):
		self.__basis = basis
		self.__space = effective_space
		self.__transform = transform
	def space(self) -> Space: return self.__space
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		for p,v in self.__basis.stream(predicate.transformed(self.__transform), environment):
			self.__transform.update(p)
			yield p,v

class Aggregation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space: Space):
		assert effective_space < basis.space()
		self.__basis = basis
		self.__space = effective_space
	def space(self) -> Space: return self.__space
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		return self.__basis.stream(predicate, environment)

class Product(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		denominator = TensorBuffer(self.__rhs, predicate, environment)
		for p,v in self.__lhs.stream(predicate, environment):
			yield p, v * denominator.get(p)

class Quotient(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		denominator = TensorBuffer(self.__rhs, predicate, environment)
		for p,v in self.__lhs.stream(predicate, environment):
			d = denominator.get(p)
			if d: yield p, v/d

class Multiplex(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, criterion:AbstractCriterion, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__criterion = criterion
		self.__rhs = rhs
	
	def space(self) -> Space: return self.__lhs.space()
	
	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		yield from self.__lhs.stream(predicate.augmented(self.__criterion), environment)
		yield from self.__rhs.stream(predicate.augmented(self.__criterion.complement()), environment)

class Filter(AbstractTensor):
	def __init__(self, basis:AbstractTensor, criterion:AbstractCriterion):
		self.__basis = basis
		self.__criterion = criterion
	
	def space(self) -> Space: return self.__basis.space()

	def stream(self, predicate: Predicate, environment:Mapping) -> Generator:
		yield from self.__basis.stream(predicate.augmented(self.__criterion), environment)


##############################################################################

class RelOp(NamedTuple):
	relop: str
	inverse: str
	fn: Callable[[Any, Any], bool]

RELOP_CATALOG = {
	'LT' : RelOp('LT', 'GE', operator.lt),
	'LE' : RelOp('LE', 'GT', operator.le),
	'EQ' : RelOp('EQ', 'NE', operator.eq),
	'NE' : RelOp('NE', 'EQ', operator.ne),
	'GE' : RelOp('GE', 'LT', operator.ge),
	'GT' : RelOp('GT', 'LE', operator.gt),
}


class Value:
	"""
	We need an abstraction covering both constants and environmental variables.
	"""
	
	def value(self, environment:Mapping) -> Any:
		raise NotImplementedError(type(self))


class ScalarComparison(AbstractCriterion):
	"""
	This is your basic scalar comparison criterion.
	Note that I'm not trying to do "between" because
		(a) the inverse would be a disjunction, and
		(b) it implies a partial order on the elements, and
		(c) it leaves open the question of range endpoints.
	Range criteria will be a separate class.
	"""
	def __init__(self, dim:str, relop:str, scalar:Value):
		# NB: These attributes are made available in case
		#     an index wants to exploit them in a manner smarter
		#     than simply testing each element in turn.
		self.dim, self.relop, self.scalar = dim, relop, scalar
		self.__space = frozenset([dim])
		self.__fn = RELOP_CATALOG[relop].fn
	
	def test(self, point: Point, environment:Mapping) -> bool:
		return self.__fn(point[self.dim], self.scalar.value(environment))
	
	def domain(self) -> Space:
		return self.__space
	
	def complement(self) -> "AbstractCriterion":
		return ScalarComparison(self.dim, RELOP_CATALOG[self.relop].inverse, self.scalar)

class Constant(Value):
	def __init__(self, value:Any): self.__value = value
	def value(self, environment:Mapping) -> Any: return self.__value

class Variable(Value):
	def __init__(self, name:str): self.__name = name
	def value(self, environment:Mapping) -> Any: return environment[self.__name]
