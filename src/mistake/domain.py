"""
Think "domain of discourse": This file should contain the bits that represent
sensible uses of data. Applications will import this to set up their schemas.

This file is still very much in KISS mode.
"""

from typing import Dict, Set

__ALL__ = ['Dimension', 'TensorType']

# Let's start with an algebra of structure spaces, with the goal of being able to
# label the space-type associated with each expression in a program.

#----------------------------------------------------------------------------------------------------

# In simplest conception, a space is a dictionary from dimensions to various control information.
# However, a particular tensor will have both data and context.

class TensorType:
	"""Simplest thing that could remotely resemble working for a limited subset of cases:"""
	# In particular, as soon as you introduce "record" types, this is inadequate.
	def __init__(self, space:Dict[str,object], context:Set[str]=frozenset()):
		self.space = space
		self.context = context
		assert not context.intersection(space.keys()), context.intersection(space.keys())
	
	def validate_for_API(self, blame:str):
		bogons = []
		for k,v in self.space.items():
			if k != k.lower(): bogons.append('%r should have been lower-case.'%k)
			if not isinstance(v, Dimension): bogons.append('%r should have been a (subclass of) <Dimension>, not %r.'%(k,type(v)))
		if bogons: raise ValueError(blame, bogons)

class Dimension:
	""" Abstract base class... """
	
