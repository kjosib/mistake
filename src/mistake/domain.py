"""
Think "domain of discourse": This file should contain the bits that represent
sensible uses of data. Applications will import this to set up their schemas.

This file is still very much in KISS mode.
"""

from typing import Iterable, Set, FrozenSet

__ALL__ = ['Dimension', 'TensorType', 'AbstractTensor']

# Let's start with an algebra of structure spaces, with the goal of being able to
# label the space-type associated with each expression in a program.

#----------------------------------------------------------------------------------------------------

# In simplest conception, a space is a dictionary from dimensions to various control information.
# However, a particular tensor will have both data and context.

class TensorType:
	"""Simplest thing that could remotely resemble working for a limited subset of cases:"""
	# In particular, as soon as you introduce "record" types, this is inadequate.
	def __init__(self, space:Set[str], context:Set[str]):
		assert isinstance(space, set), type(space)
		assert isinstance(context, set), type(context)
		self.space = space
		self.context = context
		self.e_space = space | context
		assert not self.context & self.space, self.context & self.space
	
	def validate_for_API(self, blame:str):
		bogons = []
		for k in self.space:
			if k != k.lower(): bogons.append('%r should have been lower-case.'%k)
		if bogons: raise ValueError(blame, bogons)
	

class Dimension:
	""" Abstract base class... """
	
class AbstractTensor:
	"""
	This ABC establishes the operations a tensor (expression) must support at runtime.
	At the time of this writing, there is no runtime. Ergo, there are no operations.
	However, it should be noted that this interface is not at all about storing data.
	It's entirely about retrieval (and computation) on-demand. Applications will
	generally extend this to support whatever oddball data sources they may have.
	"""

class TransformFunction:
	"""
	Various places in the language (must) support the idea of taking the ordinals of one
	dimension (or space) into another. This class answers that need.
	"""
	source_space:FrozenSet[str]
	target_space:FrozenSet[str]
	
