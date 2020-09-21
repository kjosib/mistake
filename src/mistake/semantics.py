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


class UnitOfMeasure:
	"""
	(most) Units are considered to represent a product of base-units raised to some (non-zero) power.
	In fact this conflates the roles of units and quantities, but for this exercise it's good enough.
	"""
	
	def __init__(self, powers:Dict[str,int]):
		assert all(isinstance(base_unit,str) and isinstance(exp, int) for base_unit,exp in powers.items())
		self.powers = powers
	
	def __mul__(self, other) -> "UnitOfMeasure":
		if not isinstance(other, UnitOfMeasure): return NotImplemented
		s, o, r = self.powers, other.powers, {}
		for base_unit in self.powers.keys() | other.powers.keys():
			p = s.get(base_unit,0) + o.get(base_unit,0)
			if p: r[base_unit] = p
		return UnitOfMeasure(r)
	
	def __invert__(self) -> "UnitOfMeasure":
		return UnitOfMeasure({k: -v for k,v in self.powers.items()})
	
	def __truediv__(self, other) -> "UnitOfMeasure":
		if not isinstance(other, UnitOfMeasure): return NotImplemented
		return self * ~ other
	
	def __str__(self):
		def power(x): return dim + ('^'+str(x) if x>1 else '')
		nums, dens = [], []
		for dim, exp in sorted(self.powers.items()):
			if exp > 0: nums.append(power(exp))
			else: dens.append(power(-exp))
		result = ' '.join(nums)
		if dens: result += '/' + ' '.join(dens)
		return result

dimensionless = UnitOfMeasure({})

class TensorType:
	"""
	Just a set of axes and a unit of measure at the moment.
	Later think about units of measure, stream vs. buffer, incremental vs. cumulative raster, etc.
	"""
	def __init__(self, space:Iterable[str], unit:UnitOfMeasure):
		assert isinstance(unit, UnitOfMeasure), type(unit)
		self.space = frozenset(space)
		self.unit = unit
	
	def require_perfect_symmetry(self, other:"TensorType"):
		diff = self.space.symmetric_difference(other.space)
		if diff: raise Invalid("Operand spaces do not agree about %r" % sorted(diff))

class UniverseOfDiscourse:
	"""
	A universe of discourse, in the context of the "Mistake" programming system,
	is meant to model the type-level ideas about what can possibly ever make sense.
	It can be thought of as a registry of axes, units of measure, and the
	semantic relationships between these. It is abstracted from any particular
	values, tensors, functions, etc. It's consulted mainly to see whether the
	relationships implied by value-domain operations make sense in the type-domain.
	
	It necessarily has a mapping from names to one of a few kinds of objects:
		* `Axis`
	
	Pretty soon stuff about units of measure will start to get some implementation.
	"""
	def __init__(self):
		self.lexicon = {}
	
	def __contains__(self, word:str): return word.lower() in self.lexicon
	def __getitem__(self, word:str): return self.lexicon[word.lower()]
	def __enter(self, word, entry):
		if word in self: raise Invalid("This word %r already has a definition."%word)
		self.lexicon[word.lower()] = entry

	def register_axis(self, axis:Axis):
		assert isinstance(axis, Axis)
		if isinstance(axis, Axis):
			missing = axis.requires - self.lexicon.keys()
			if missing: raise Invalid("This axis requires yet-undefined axes: %r"%missing)
		self.__enter(axis.name, axis)
	
	def create_fundamental_unit(self, name:str) -> UnitOfMeasure:
		assert isinstance(name, str)
		unit = UnitOfMeasure({name:1})
		self.__enter(name, unit)
		return unit
