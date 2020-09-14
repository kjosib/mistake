"""
This submodule should implement the central abstractions for semantic checking.
In the beginning, this was the whole "equivalent-space tensor" idea.
Note there is zero run-time here (on purpose): This is all about the calculation
of whether an expression will make semantic sense. In other words, these are the
type-domain computations factored away and organized into a module.

At the moment, the refactoring to create this file is just getting started.
"""
from typing import Set, FrozenSet, Iterable, Tuple

class Invalid(Exception):
	""" One generic exception for invalid semantics, with a string error code. Good enough for now.  """
	def __init__(self, message:str): self.message = message


class Dimension:
	""" Abstract base class... """



class TensorType:
	"""
	Just provide the set of dimensions at the moment.
	Later think about units of measure, stream vs. buffer, incremental vs. cumulative raster, etc.
	"""
	def __init__(self, space:Iterable[str]):
		self._space = frozenset(space)
	
	def require_perfect_symmetry(self, other:"TensorType"):
		diff = self._space.symmetric_difference(other._space)
		if diff: raise Invalid("Operand spaces do not agree about %r" % diff)
