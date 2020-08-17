"""
Change of Plans:

Instead of ONLY performing semantic validation in one pass, the new thinking is to
integrate validation with query planning.

Everything in this module is about static analysis:
determining whether the elements of a program are semantically
sound -- or if otherwise, localizing the inconsistencies for easy
diagnosis and repair.
"""
import operator
from typing import Callable, Iterable
from boozetools.support import foundation
from . import frontend, runtime
from .domain import AbstractTensor, Universe

class Invalid(Exception):
	""" Arguments are span and message. """
	def gripe(self, how): how(*self.args[0], message=self.args[1])

class Planner(foundation.Visitor):
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
		assert isinstance(lhs, AbstractTensor) and isinstance(rhs, AbstractTensor)
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
		dim = m.criterion.axis
		lhs, rhs = self.__symmetric_types(m.if_true, dim.span, m.if_false)
		if dim.text not in lhs.space(): _unavailable(dim, lhs.space())
		return runtime.Multiplex(lhs, self.__make_predicate(dim.text, m.criterion.relop, m.criterion.scalar), rhs)
	
	def __make_predicate(self, dim, relop, scalar):
		# TODO: make this into something that can drive query optimization.
		op = {
			'LT': operator.lt,
			'LE': operator.le,
			'EQ': operator.eq,
			'NE': operator.ne,
			'GE': operator.ge,
			'GT': operator.gt,
		}[relop]
		return lambda point:op(point[dim], scalar)
	
	def visit_Aggregation(self, agg:frontend.Aggregation):
		basis = self.visit(agg.a_exp)
		if isinstance(basis, Invalid): return basis
		assert isinstance(basis, AbstractTensor), [type(agg.a_exp), type(basis)]
		new_space = set()
		for dim in agg.new_space:
			if dim.text in new_space: _already(dim)
			if dim.text not in basis.space(): _unavailable(dim, basis.space())
			new_space.add(dim.text)
		# TODO: At this point, in theory we could have an invalid aggregation. However, I don't have the means to check yet.
		
		return runtime.Aggregation(basis, new_space)
	
	def visit_Name(self, n:frontend.Name) -> AbstractTensor:
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
		assert isinstance(basis, AbstractTensor), type(basis)
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
			# Next, do we have a registered function in the environment to perform this translation?
			domain = frozenset(dim.text for dim in mx.domain)
			range_ = frozenset(dim.text for dim in mx.range)
			step = self.__universe.find_transform(domain, range_)
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
		return runtime.Transformation(basis, effective_space, procedure)

def _unavailable(dim:frontend.Name, ops:Iterable[str]):
	raise Invalid(dim.span, "Dimension %r is not available here. options are %r." % (dim.text, sorted(ops)))

def _already(dim:frontend.Name):
	raise Invalid(dim.span, "Dimension %r is already present and may not be duplicated."%dim.text)

def _sequence(procedure, step):
	if procedure is None: return step
	def two_step(p): procedure(p); step(p)
	return two_step
