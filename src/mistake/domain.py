"""
Think "domain of discourse": This file should contain the bits that represent
sensible uses of data. Applications will import this to set up their schemas.

This file is still very much in KISS mode.
"""

from typing import AbstractSet, FrozenSet, Dict, NamedTuple, Callable, Generator, Mapping, MutableMapping

__ALL__ = ['Dimension', 'TensorType', 'AbstractTensor', 'Universe', 'AlreadyRegistered', 'RandomAccessTensor']

Space = AbstractSet[str]

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
	domain: FrozenSet[str]
	range: FrozenSet[str]
	def validate_for_API(self):
		_validate_space(self.domain)
		_validate_space(self.range)
		assert self.range
		
			

class Universe:
	"""
	Think of this as like a schema for a database. A "universe of discourse" has
		1. a mapping from names to `Dimension` objects,
		2. a registry of `TransformFunction` objects,
		3. a registry of `AbstractTensor` objects.
	"""
	
	__dims: Dict[str,Dimension]
	__transforms: Dict[Transform, Callable[[Dict], Dict]]
	__tensors: Dict[str, AbstractTensor]
	
	def __init__(self, dims:Dict[str,Dimension]):
		for k,v in dims.items():
			assert k == k.lower(), "Dimension %r should have been lower-case."%k
			assert isinstance(v, Dimension), "Oops! Dimension %r is mistakenly %r."%(k, type(v))
		self.__dims = dims
		self.__transforms = {}
		self.__tensors = {}
	
	def register_transform(self, domain:Space, range_:Space, transform:Callable[[MutableMapping], None]):
		transform_type = Transform(frozenset(domain), frozenset(range_))
		transform_type.validate_for_API()
		if transform_type in self.__transforms: raise AlreadyRegistered(transform_type)
		assert callable(transform)
		self.__transforms[transform_type] = transform
	
	def register_attribute(self, domain:str, range_:str, function):
		def transform(p): p[range_] = function(p[domain])
		self.register_transform({domain}, {range_}, transform)
	
	def register_tensor(self, name:str, tensor:AbstractTensor):
		if name != name.lower(): raise ValueError(name)
		if name in self.__tensors: raise AlreadyRegistered(name)
		assert isinstance(tensor, AbstractTensor), type(tensor)
		self.__tensors[name] = tensor
	
	def tensor_types(self) -> Dict[str, Space]:
		return {name:tensor.space() for name, tensor in self.__tensors.items()}

	def find_transform(self, domain:Space, range_:Space):
		return self.__transforms.get(Transform(frozenset(domain), frozenset(range_)))
	
	def get_tensor(self, name:str):
		return self.__tensors[name]
	