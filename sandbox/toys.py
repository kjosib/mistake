"""
Of course a sandbox is much enhanced by the provision of toys.
The better toys may be promoted to proper members of the toolkit.

These toys are meant for experimentation:
	Neither organization nor documentation are assured.
"""

from typing import Dict, Set

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
		bogons = [k for k in self.space if k != k.lower()]
		assert not bogons, "For %r, dimensions should be lower-case. This includes %r"%(blame, sorted(bogons))

#----------------------------------------------------------------------------------------------------

# There's a big difference between type and storage-class. The former is about theory and semantics.
# The latter is about the concrete organization of data for storage and retrieval with particular
# space and time characteristics.

# Let's posit a simple storage class:

class TensorValue:
	""" This is sort of a default "simplest conceivable" storage class """
	def __init__(self, tt:TensorType, context:Dict[str, object]=()):
		self.tt = tt
		self.context = dict(context)
		assert self.context.keys() == tt.context # Semantic validation should prove this.
		self.__storage = {}
		self.__schedule = tuple(self.tt.space)

	def __key(self, point:dict) -> tuple:
		# We can worry about the VALIDITY of keys later.
		return tuple(point[k] for k in self.__schedule)

	def get(self, point): return self.__storage.get(self.__key(point), 0)

	def set(self, point, value): self.__storage[self.__key(point)] = value
	
	def increment(self, point, value):
		key = self.__key(point)
		self.__storage[key] = self.__storage.get(key, 0) + value
	
	def items(self):
		for key,value in self.__storage.items():
			yield dict(zip(self.__schedule, key)), value

