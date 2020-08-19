"""
Think "domain of discourse": This file should contain the bits that represent
sensible uses of data. Applications will import this to set up their schemas.

This file is still very much in KISS mode.
"""

from typing import Dict, NamedTuple, Callable, Generator, Any, Tuple, FrozenSet, Iterable

__ALL__ = ['Dimension', 'TensorType', 'AbstractTensor', 'Universe', 'AlreadyRegistered', 'RandomAccessTensor']

Space = FrozenSet[str]
Point = Dict[str, Any]

class AlreadyRegistered(Exception):
	""" Lots of places maybe don't like to reuse the same names for different things. """

def _validate_space(space:Space):
	for d in space:
		if not (isinstance(d, str)): raise TypeError('should have been string', type(d))
		if d != d.lower(): raise ValueError('should have been lower-case', d)

# Let's start with an algebra of structure spaces, with the goal of being able to
# label the space-type associated with each expression in a program.

#----------------------------------------------------------------------------------------------------

# In simplest conception, a space is a dictionary from dimensions to various control information.
# However, a particular tensor will have both data and context.


class Dimension:
	""" Abstract base class... """

class AbstractTensor:
	"""
	This ABC establishes the operations a tensor (expression) must support at runtime.
	At the moment, the runtime is mostly hypothetical. Ergo, operations are minimal.
	
	Heed: this interface is principally about retrieval (and computation) on-demand,
	not intermediate data storage. Applications will generally extend this to support
	whatever oddball data sources they may have.
	
	The runtime module must provide implementations for (so-to-speak) "query plans".
	"""
	
	def space(self) -> Space:
		raise NotImplementedError(type(self))
	
	def stream(self) -> Generator:
		"""
		The current operational thinking is to yield "point-value" pairs.
		In the extremely short run, this might get something (inefficient) off the ground.
		Later it will be important to think about indexing and pushing queries back closer
		to the source data.
		"""
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
	def validate_for_API(self):
		_validate_space(self.domain)
		_validate_space(self.range)
		assert self.range


class AbstractCriterion:
	"""
	Let's get the basic operations down.
	"""
	
	def test(self, point: Point) -> bool:
		raise NotImplementedError(type(self))
	
	def domain(self) -> Space:
		raise NotImplementedError(type(self))


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
	
	def test(self, point: Point) -> bool:
		return all(criterion.test(point) for criterion in self.__criteria)


class Universe:
	"""
	Think of this as like a schema for a database. A "universe of discourse" has
		1. a mapping from names to `Dimension` objects,
		2. a registry of `TransformFunction` objects,
		3. a registry of `AbstractTensor` objects.
	"""
	
	__dims: Dict[str,Dimension]
	__transforms: Dict[Tuple[FrozenSet, FrozenSet], Transform]
	__tensors: Dict[str, AbstractTensor]
	
	def __init__(self, dims:Dict[str,Dimension]):
		for k,v in dims.items():
			assert k == k.lower(), "Dimension %r should have been lower-case."%k
			assert isinstance(v, Dimension), "Oops! Dimension %r is mistakenly %r."%(k, type(v))
		self.__dims = dims
		self.__transforms = {}
		self.__tensors = {}
	
	def register_transform(self, transform:Transform):
		transform.validate_for_API()
		key = (frozenset(transform.domain), frozenset(transform.range)) ## Defensive programming? Meh.
		if key in self.__transforms: raise AlreadyRegistered(key)
		else: self.__transforms[key] = transform
	
	def register_attribute(self, domain:str, range_:str, function):
		def update(p): p[range_] = function(p[domain])
		transform = Transform(frozenset((domain,)), frozenset((range_,)), update)
		self.register_transform(transform)
	
	def register_tensor(self, name:str, tensor:AbstractTensor):
		if name != name.lower(): raise ValueError(name)
		if name in self.__tensors: raise AlreadyRegistered(name)
		assert isinstance(tensor, AbstractTensor), type(tensor)
		self.__tensors[name] = tensor
	
	def tensor_types(self) -> Dict[str, Space]:
		return {name:tensor.space() for name, tensor in self.__tensors.items()}

	def find_transform(self, domain:Space, range_:Space):
		key = (frozenset(domain), frozenset(range_))
		return self.__transforms.get(key)
	
	def get_tensor(self, name:str):
		return self.__tensors[name]
	