"""
Elements of the runtime are (for now, at least) principally implementations of
AbstractTensor which work by sifting, filtering, and combining other Tensor objects.

Continuing to KEEP IT SIMPLE, SALLY!
"""
from typing import Generator, Callable, Mapping, Iterable, Tuple
from .domain import Space, Point, AbstractTensor, Transform, AbstractCriterion, Predicate

class TensorBuffer:
	"""
	I'm making an adjustment: henceforth a TensorBuffer is just an implementation
	detail for other (streaming) tensors. Seen another way, the TensorBuffer is
	involved in things that look more like "reduce", whereas the AbstractTensor
	hierarchy has the "map" role.
	
	For now this bit remains somewhat simplistic.
	"""
	
	def __init__(self, upstream:AbstractTensor, predicate:Predicate):
		self.__upstream = upstream
		self.__storage = {}
		self.__schedule = tuple(upstream.space())
		for point, value in self.__upstream.stream(predicate):
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
	
	def stream(self, predicate:Predicate) -> Generator:
		# Note this could possibly yield increments to the same point twice. That's OK because
		# points are incremental -- at least under the assumption that everything else is...
		yield from self.__lhs.stream(predicate)
		yield from self.__rhs.stream(predicate)

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
	
	def stream(self, predicate:Predicate) -> Generator:
		for p, v in self.__basis.stream(predicate):
			yield p, v * self.__factor

class Transformation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space:Space, transform:Transform):
		self.__basis = basis
		self.__space = effective_space
		self.__transform = transform
	def space(self) -> Space: return self.__space
	def stream(self, predicate:Predicate) -> Generator:
		for p,v in self.__basis.stream(predicate.transformed(self.__transform)):
			self.__transform.update(p)
			yield p,v

class Aggregation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space: Space):
		assert effective_space < basis.space()
		self.__basis = basis
		self.__space = effective_space
	def space(self) -> Space: return self.__space
	def stream(self, predicate:Predicate) -> Generator:
		return self.__basis.stream(predicate)

class Product(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self, predicate:Predicate) -> Generator:
		denominator = TensorBuffer(self.__rhs, predicate)
		for p,v in self.__lhs.stream(predicate):
			yield p, v * denominator.get(p)

class Quotient(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self, predicate:Predicate) -> Generator:
		denominator = TensorBuffer(self.__rhs, predicate)
		for p,v in self.__lhs.stream(predicate):
			d = denominator.get(p)
			if d: yield p, v/d

class Multiplex(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, criteron:AbstractCriterion, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__criteron = criteron
		self.__rhs = rhs
	
	def space(self) -> Space: return self.__lhs.space()
	
	def stream(self, predicate:Predicate) -> Generator:
		yield from self.__lhs.stream(predicate.augmented(self.__criteron))
		yield from self.__rhs.stream(predicate.augmented(self.__criteron.inverted()))



