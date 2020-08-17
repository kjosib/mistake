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
from typing import Callable, Union
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
		if isinstance(lhs, Invalid): return lhs
		if isinstance(rhs, Invalid): return rhs
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
		if dim.text not in lhs.space():
			raise Invalid(dim.span, "Dimension %r is not available here. options are %r."%(dim.text, sorted(lhs.space())))
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
			if dim.text in new_space: raise Invalid(dim.span, "Dimension was mentioned earlier in the same list.")
			if dim.text not in basis.space():raise Invalid(dim.span, "Dimension %r is not available here. options are %r."%(dim.text, sorted(basis.space())))
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

	def visit_SumImage(self, si:frontend.SumImage):
		# Checking type is a bit easier than doing an optimal grouping, because
		# ideally you'd like to compute the transforms in parallel to avoid
		# making multiple passes through the data.
		a_expr = self.visit(si.a_exp)
		for mx in si.sums:
			if isinstance(a_expr, Invalid): return a_expr
			assert isinstance(a_expr, AbstractTensor), type(a_expr)
			a_expr = self.__apply_one_transform(a_expr, mx)
		return a_expr
	
	def __apply_one_transform(self, a_expr:AbstractTensor, mx:frontend.MappingExpression) -> Union[runtime.Transformation, Invalid]:
		# First, apply a simple textual test:
		effective_space = set(a_expr.space())
		for dim in mx.domain:
			try: effective_space.remove(dim.text)
			except KeyError: raise Invalid(dim.span, "Dimension %r is not available here. options are %r." % (dim.text, sorted(effective_space)))
		for dim in mx.range:
			if dim.text in effective_space: raise Invalid(dim.span, "Dimension %r is already present in the input tensor."%dim.text)
			else: effective_space.add(dim.text)
		
		# Next, do we have a registered function in the environment to perform this translation?
		domain = frozenset(dim.text for dim in mx.domain)
		range_ = frozenset(dim.text for dim in mx.range)
		
		function = self.__universe.find_transform(domain, range_)
		if function is None:
			raise Invalid(mx.op_span, "No known transform applies.")
		
		return runtime.Transformation(a_expr, effective_space, function)


