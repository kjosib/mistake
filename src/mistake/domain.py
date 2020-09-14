"""
Think "domain of discourse": This file should contain the bits that represent
sensible uses of data. Applications will import this to set up their schemas.

This file is still very much in KISS mode.
It also stands a very good chance of completely dissipating into other modules.
"""

from typing import Dict, NamedTuple, Callable, Generator, Any, Tuple, FrozenSet, Iterable, Mapping
from . import semantics

Space = FrozenSet[str]
Point = Dict[str, Any]


# Let's start with an algebra of structure spaces, with the goal of being able to
# label the space-type associated with each expression in a program.

#----------------------------------------------------------------------------------------------------

# In simplest conception, a space is a dictionary from dimensions to various control information.
# However, a particular tensor will have both data and context.


class AbstractTensor:
	"""
	This ABC establishes the operations a tensor (expression) must support at runtime.
	At the moment, the runtime is mostly hypothetical. Ergo, operations are minimal.
	
	Heed: this interface is principally about retrieval (and computation) on-demand,
	not intermediate data storage. Applications will generally extend this to support
	whatever oddball data sources they may have.
	
	The runtime module must provide implementations for (so-to-speak) "query plans".
	"""
	
	def tensor_type(self) -> semantics.TensorType:
		raise NotImplementedError(type(self))
	
	def stream(self, predicate:"Predicate", environment:Mapping) -> Generator:
		"""
		The current operational thinking is to yield "point-value" pairs.
		In the extremely short run, this might get something (inefficient) off the ground.
		Later it will be important to think about indexing and pushing queries back closer
		to the source data.
		
		This method must respect the predicate. It is free to use any suitable means.
		However, if this tensor works by delegation, it may also delegate that responsibility.
		"""
		raise NotImplementedError(type(self))


class AbstractCriterion:
	"""
	Let's get the basic operations down.
	"""
	
	def test(self, point: Point, environment:Mapping) -> bool:
		raise NotImplementedError(type(self))
	
	def domain(self) -> Space:
		raise NotImplementedError(type(self))
	
	def complement(self) -> "AbstractCriterion":
		raise NotImplementedError(type(self))


class Transform(NamedTuple):
	"""
	Describes the type of a function from points in one space to points in another.
	In geometric applications these spaces be the same, but that's not my main idea.
	I'm thinking more like "OrderID -> ShipCountry" or "Date -> Month".
	"""
	domain: Space
	range: Space
	update: Callable[[Point], None]


class TranslatedCriterion(AbstractCriterion):
	"""
	This would be used by Transformation nodes.

	Still in KISS mode, this may result in a given translation being
	performed more than once, but again for the moment the resource
	to be optimized is programmer time (and brainpower), not cycles.
	"""
	
	def __init__(self, transform: Transform, basis: AbstractCriterion):
		self.__transform = transform
		self.__basis = basis
	
	def test(self, point: Point, environment:Mapping) -> bool:
		self.__transform.update(point)
		return self.__basis.test(point, environment)
	
	def domain(self) -> Space:
		return self.__transform.domain
	
	def complement(self) -> AbstractCriterion:
		return TranslatedCriterion(self.__transform, self.__basis.complement())


class Predicate:
	"""
	Presumably a predicate is just a collection of zero-or-more criteria.
	"""
	
	def __init__(self, criteria: Iterable[AbstractCriterion]):
		self.__criteria = list(criteria)
	
	def divmod(self, divisor: Space) -> Tuple["Predicate", "Predicate"]:
		"""
		This is in support of indexes. The idea is to skip loading blocks of data
		that won't ultimately contribute to the answer to some query.
		The "divisor" parameter represents the space over which your index is defined.
		Then, you can use the quotient on the index and the modulus on the individual
		data elements within selected index blocks.
		"""
		quotient, modulus = [], []
		for criterion in self.__criteria:
			(quotient if criterion.domain().issubset(divisor) else modulus).append(criterion)
		return Predicate(quotient), Predicate(modulus)
	
	def test(self, point: Point, environment:Mapping) -> bool:
		return all(criterion.test(point, environment) for criterion in self.__criteria)
	
	def augmented(self, criterion:AbstractCriterion):
		return Predicate(self.__criteria + [criterion])
	
	def transformed(self, transform:Transform):
		# TODO: This is very simplistic. A given transform might have a better way to
		#  handle the problem. However, that's not important for a first version.
		return Predicate([
			TranslatedCriterion(transform, c) if transform.range & c.domain() else c
			for c in self.__criteria
		])


