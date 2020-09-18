"""
This submodule should implement the central abstractions for semantic checking.
In the beginning, this was the whole "equivalent-space tensor" idea.
Note there is zero run-time here (on purpose): This is all about the calculation
of whether an expression will make semantic sense. In other words, these are the
type-domain computations factored away and organized into a module.

At the moment, the goal is to support interesting characteristics of Axis objects.
"""
import operator, enum
from typing import Set, FrozenSet, Iterable, Dict, NamedTuple, Callable, List

class Invalid(Exception):
	""" One generic exception for invalid semantics, with a string error code. Good enough for now.  """
	def __init__(self, message:str): self.message = message

class Axis:
	"""
	Roughly analogous to a (partial) relational key.
	"""
	def __init__(self, *, name=None, requires: Iterable[str] = ()):
		self.name = name or self.__class__.__name__
		self.requires = frozenset(map(str.lower, requires)) # Refuse to be in a space without required other dimensions.
	
	def show(self, member):
		""" Override to control textual presentation of members """
		return str(member)
	
	def sort_key(self, member):
		""" Override to control natural ordering of members """
		return member
	
	def array(self, attested_members):
		"""
		Override to control how lists of members are gathered and presented.
		In particular, you may wish an affine axis to fill gaps in a range.
		"""
		return sorted(set(attested_members), key=self.sort_key)


class FundamentalUnit(NamedTuple):
	name:str
	fundamental_quantity:str # For instance dollars and euros are both money; feet and meters are both distance.

class DerivedUnit(NamedTuple):
	name:str
	#

class TensorType:
	"""
	Just provide the set of dimensions at the moment.
	Later think about units of measure, stream vs. buffer, incremental vs. cumulative raster, etc.
	"""
	def __init__(self, space:Iterable[str]):
		self._space = frozenset(space)
	
	def require_perfect_symmetry(self, other:"TensorType"):
		diff = self._space.symmetric_difference(other._space)
		if diff: raise Invalid("Operand spaces do not agree about %r" % sorted(diff))

class UniverseOfDiscourse:
	"""
	A universe of discourse, in the context of the "Mistake" programming system,
	is meant to model the type-level ideas about what can possibly ever make sense.
	It can be thought of as a registry of dimensions, units of measure, and the
	semantic relationships between these. It is abstracted from any particular
	values, tensors, functions, etc. It's consulted mainly to see whether the
	relationships implied by value-domain operations make sense in the type-domain.
	
	It necessarily has a mapping from names to one of a few kinds of objects:
		* `Axis`
		* `FundamentalUnit`
		* `DerivedUnit`
	
	Pretty soon stuff about units of measure will start to get some implementation.
	"""
	def __init__(self):
		self.lexicon = {}
	
	def __contains__(self, word:str): return word.lower() in self.lexicon
	def __getitem__(self, word:str): return self.lexicon[word.lower()]
	
	def enter(self, entry):
		assert isinstance(entry, (Axis, FundamentalUnit, DerivedUnit))
		word = entry.name
		if word in self: raise Invalid("This word %r already has a definition."%word)
		if isinstance(entry, Axis):
			missing = entry.requires - self.lexicon.keys()
			if missing: raise Invalid("This axis requires yet-undefined axes: %r"%missing)
		self.lexicon[word.lower()] = entry
	
