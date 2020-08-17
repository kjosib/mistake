"""
Elements of the runtime are (for now, at least) principally implementations of
AbstractTensor which work by sifting, filtering, and combining other Tensor objects.

Continuing to KEEP IT SIMPLE, SALLY!
"""
from typing import Generator, Callable, Mapping
from .domain import Space, AbstractTensor, Transform

class TensorBuffer(AbstractTensor):
	""" Simplest conceivable storage class """
	
	def __init__(self, *, space):
		self.__storage = {}
		self.__schedule = tuple(space)
	
	def space(self) -> Space: return frozenset(self.__schedule)
	
	def __key(self, point) -> tuple:
		# We can worry about the VALIDITY of keys later.
		return tuple(point[k] for k in self.__schedule)
	
	def get(self, point): return self.__storage.get(self.__key(point), 0)
	
	def set(self, point, value): self.__storage[self.__key(point)] = value
	
	def increment(self, point, value):
		key = self.__key(point)
		self.__storage[key] = self.__storage.get(key, 0) + value
	
	def stream(self) -> Generator:
		for key, value in self.__storage.items():
			yield dict(zip(self.__schedule, key)), value
	
	def accumulate(self, tensor:AbstractTensor):
		for point, value in tensor.stream():
			self.increment(point, value)
		return self
	
	def buffer(self): return self
	
	@staticmethod
	def wrap(tensor:AbstractTensor) -> AbstractTensor:
		if hasattr(tensor, 'get'): return tensor
		if hasattr(tensor, 'buffer'): return tensor.buffer()
		else: return TensorBuffer(space=tensor.space()).accumulate(tensor)
	

class SumTensor(AbstractTensor):
	""" Simplest possible "work-flow" class """
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
		if hasattr(lhs, 'get') and hasattr(rhs, 'get'):
			self.get = lambda point: lhs.get(point) + rhs.get(point)
	
	def space(self) -> Space: return self.__lhs.space()
	
	def buffer(self) -> TensorBuffer:
		return TensorBuffer(space=self.space()).accumulate(self.__lhs).accumulate(self.__rhs)

	def stream(self) -> Generator: return self.buffer().stream()

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
	
	def stream(self) -> Generator:
		for p, v in self.__basis.stream():
			yield p, v * self.__factor

class Transformation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space:Space, transform:Callable[[Mapping],None]):
		self.__basis = basis
		self.__space = effective_space
		self.__transform = transform
	def space(self) -> Space: return self.__space
	def stream(self) -> Generator: return self.buffer().stream()
	def buffer(self) -> TensorBuffer:
		result = TensorBuffer(space=self.__space)
		for p,v in self.__basis.stream():
			self.__transform(p)
			result.increment(p,v)
		return result

class Aggregation(AbstractTensor):
	def __init__(self, basis: AbstractTensor, effective_space: Space):
		self.__basis = basis
		self.__space = effective_space
	def space(self) -> Space: return self.__space
	def stream(self) -> Generator: return self.buffer().stream()
	def buffer(self) -> TensorBuffer:
		return TensorBuffer(space=self.__space).accumulate(self.__basis)

class Product(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self) -> Generator:
		denominator = TensorBuffer.wrap(self.__rhs)
		for p,v in self.__lhs.stream():
			yield p, v * denominator.get(p)
	
	def buffer(self) -> TensorBuffer:
		return TensorBuffer(space=self.space()).accumulate(self)

class Quotient(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, rhs:AbstractTensor):
		self.__lhs = lhs
		self.__rhs = rhs
	def space(self) -> Space: return self.__lhs.space()
	def stream(self) -> Generator:
		denominator = TensorBuffer.wrap(self.__rhs)
		for p,v in self.__lhs.stream():
			d = denominator.get(p)
			if d: yield p, v/d
	
	def buffer(self) -> TensorBuffer:
		return TensorBuffer(space=self.space()).accumulate(self)

class Multiplex(AbstractTensor):
	def __init__(self, lhs:AbstractTensor, predicate:Callable[[dict],bool], rhs:AbstractTensor):
		self.__lhs = lhs
		self.__predicate = predicate
		self.__rhs = rhs
	
	def space(self) -> Space: return self.__lhs.space()
	
	def stream(self) -> Generator:
		for p,v in self.__lhs.stream():
			if self.__predicate(p): yield p,v
		for p,v in self.__rhs.stream():
			if not self.__predicate(p): yield p,v
