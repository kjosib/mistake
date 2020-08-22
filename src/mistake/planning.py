"""
This is turning into the API submodule for
"""

from typing import Callable, Iterable, Dict, Tuple, FrozenSet
from boozetools.support import foundation
from . import frontend, runtime, domain

__ALL__ = ['Universe', 'AlreadyRegistered']

class AlreadyRegistered(Exception):
	""" The key for some sort of registration API call has already been used in a previous call. """


class Universe:
	"""
	Think of this as like a schema for a database. A "universe of discourse" has
		1. a mapping from names to `Dimension` objects,
		2. a registry of `TransformFunction` objects,
		3. a registry of `AbstractTensor` objects.
	"""
	
	__dims: Dict[str,domain.Dimension]
	__transforms: Dict[Tuple[FrozenSet, FrozenSet], domain.Transform]
	__tensors: Dict[str, domain.AbstractTensor]
	
	def __init__(self, dims:Dict[str,domain.Dimension]):
		for k,v in dims.items():
			assert k == k.lower(), "Dimension %r should have been lower-case."%k
			assert isinstance(v, domain.Dimension), "Oops! Dimension %r is mistakenly %r."%(k, type(v))
		self.__dims = dims
		self.__transforms = {}
		self.__tensors = {}
	
	def register_transform(self, transform:domain.Transform):
		transform.validate_for_API()
		key = (frozenset(transform.domain), frozenset(transform.range)) ## Defensive programming? Meh.
		if key in self.__transforms: raise AlreadyRegistered(key)
		else: self.__transforms[key] = transform
	
	def register_attribute(self, domain_:str, range_:str, function):
		def update(p): p[range_] = function(p[domain_])
		transform = domain.Transform(frozenset((domain_,)), frozenset((range_,)), update)
		self.register_transform(transform)
	
	def register_tensor(self, name:str, tensor:domain.AbstractTensor):
		if name != name.lower(): raise ValueError(name)
		if name in self.__tensors: raise AlreadyRegistered(name)
		assert isinstance(tensor, domain.AbstractTensor), type(tensor)
		self.__tensors[name] = tensor
	
	def tensor_types(self) -> Dict[str, domain.Space]:
		return {name:tensor.space() for name, tensor in self.__tensors.items()}

	def find_transform(self, domain_:Iterable[str], range_:Iterable[str]):
		key = (frozenset(domain_), frozenset(range_))
		return self.__transforms.get(key)
	
	def get_tensor(self, name:str):
		return self.__tensors[name]
	
	def query(self, name:str):
		return runtime.TensorBuffer(self.get_tensor(name.lower()), domain.Predicate([]))

	def script(self, text:str):
		""" Call this to parse and load a script full of definitions. """
		parser = frontend.Parser()
		ast = parser.parse(text)
		if ast is not None:
			Planner(self, parser.source.complain).visit(ast)
		return self

class Invalid(Exception):
	""" Arguments are span and message. """
	def gripe(self, how): how(*self.args[0], message=self.args[1])


class Planner(foundation.Visitor):
	"""
	This class integrates semantic validation with query planning.
	It converts AST nodes (from the parser) into a suitable run-time
	structure concurrent with static analysis to determine whether
	the elements of each definition have sound semantics -- and if
	otherwise, then localizing the inconsistencies for easy
	diagnosis and repair.
	"""
	def __init__(self, universe:Universe, complain:Callable, verbose=False):
		self.__universe = universe
		self.__complain = complain
		self.__verbose = verbose
		self.__type_env = universe.tensor_types()
		
	def visit_list(self, items):
		for i in items: self.visit(i)
	
	def visit_DefineTensor(self, dt:frontend.DefineTensor):
		if dt.name.text in self.__type_env:
			self.__complain(*dt.name.span, message="Tensor name was previously defined; ignoring redefinition.")
		else:
			try: tensor = self.visit(dt.expr)
			except Invalid as e:
				self.__complain(*dt.name.span, message="Tensor value has invalid spatial type, because...")
				e.gripe(self.__complain)
				space = None
			else:
				self.__universe.register_tensor(dt.name.text, tensor) # Contains type assertion.
				space = tensor.space()
				if self.__verbose: print(dt.name.text, 'has shape', sorted(space))
			self.__type_env[dt.name.text] = space
	
	def __symmetric_types(self, lhs_exp, op_span, rhs_exp):
		lhs = self.visit(lhs_exp)
		rhs = self.visit(rhs_exp)
		assert isinstance(lhs, domain.AbstractTensor) and isinstance(rhs, domain.AbstractTensor)
		if lhs.space() == rhs.space():
			return lhs, rhs
		else:
			diff = set(lhs.space()).symmetric_difference(rhs.space())
			raise Invalid(op_span, "Operand spaces do not agree about %r"%diff)
	
	def visit_TensorSum(self, d: frontend.TensorSum): return runtime.SumTensor(*self.__symmetric_types(*d))
	def visit_Difference(self, d: frontend.Difference): return runtime.difference(*self.__symmetric_types(*d))
	def visit_Product(self, d: frontend.Product): return runtime.Product(*self.__symmetric_types(*d))
	def visit_Quotient(self, d: frontend.Difference): return runtime.Quotient(*self.__symmetric_types(*d))
	
	def visit_Multiplex(self, m:frontend.Multiplex):
		lhs, rhs = self.__symmetric_types(m.if_true, m.criterion.axis.span, m.if_false)
		return runtime.Multiplex(lhs, self.visit(m.criterion, lhs.space()), rhs)
	
	def visit_Filter(self, f:frontend.Filter):
		basis = self.visit(f.basis)
		return runtime.Filter(basis, self.visit(f.criterion, basis.space()))
	
	def visit_Criterion(self, c:frontend.Criterion, space:domain.Space) -> runtime.RelopCriterion:
		if c.axis.text not in space: _unavailable(c.axis, space)
		# TODO: Compare the argument and the relation to the type of the dimension.
		return runtime.RelopCriterion(c.axis.text, c.relop, c.scalar)
	
	def visit_Aggregation(self, agg:frontend.Aggregation):
		basis = self.visit(agg.a_exp)
		if isinstance(basis, Invalid): return basis
		assert isinstance(basis, domain.AbstractTensor), [type(agg.a_exp), type(basis)]
		new_space = set()
		for dim in agg.new_space:
			if dim.text in new_space: _already(dim)
			if dim.text not in basis.space(): _unavailable(dim, basis.space())
			new_space.add(dim.text)
		# TODO: At this point, in theory we could have an invalid aggregation. However, I don't have the means to check yet.
		#  To clarify: Either a dimension might not be safe to sum over (yet we did) or a remaining dimension may
		#  be strictly subordinate to one we DID sum over.
		return runtime.Aggregation(basis, new_space)
	
	def visit_Name(self, n:frontend.Name) -> domain.AbstractTensor:
		try: return self.__universe.get_tensor(n.text)
		except KeyError:
			if n.text in self.__type_env: raise (n.span, "ill-typed name.")
			else: raise Invalid(n.span, "undefined name.")
	
	def visit_ScaleBy(self, s:frontend.ScaleBy):
		return self.visit(s.a_exp)

	def visit_SumImage(self, si:frontend.SumImage) -> runtime.Transformation:
		# Ideally you'd like to compute the transforms in parallel to avoid
		# making multiple passes through the data.
		basis = self.visit(si.a_exp)
		assert isinstance(basis, domain.AbstractTensor), type(basis)
		effective_space = set(basis.space())
		procedure = None
		for mx in si.sums:
			# First, apply a simple textual test:
			for dim in mx.domain:
				try: effective_space.remove(dim.text)
				except KeyError: _unavailable(dim, effective_space)
			for dim in mx.range:
				if dim.text in effective_space: _already(dim)
				else: effective_space.add(dim.text)
			# Next, do we have a registered function in the "universe" to perform this translation?
			def texts(names): return [n.text for n in names]
			step = self.__universe.find_transform(texts(mx.domain), texts(mx.range))
			if step is None: raise Invalid(mx.op_span, "No known transform applies.")
			procedure = _sequence(procedure, step)
		# Last step: Consider any explicit aggregation. (See also visit_Aggregation.)
		if si.space is not None:
			new_space = set()
			for dim in si.space:
				if dim.text in new_space: _already(dim)
				if dim.text not in effective_space: _unavailable(dim, effective_space)
				new_space.add(dim.text)
			effective_space = new_space
		return runtime.Transformation(basis, frozenset(effective_space), procedure)

def _unavailable(dim:frontend.Name, ops:Iterable[str]):
	raise Invalid(dim.span, "Dimension %r is not available here. options are %r." % (dim.text, sorted(ops)))

def _already(dim:frontend.Name):
	raise Invalid(dim.span, "Dimension %r is already present and may not be duplicated."%dim.text)

def _sequence(procedure, step):
	if procedure is None: return step
	def two_step(p): procedure(p); step(p)
	return two_step
