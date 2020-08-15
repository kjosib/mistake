"""
Everything in this module is about static analysis:
determining whether the elements of a program are semantically
sound -- or if otherwise, localizing the inconsistencies for easy
diagnosis and repair.
"""

from typing import Callable, Union
from boozetools.support import foundation
from . import frontend
from .domain import TensorType, AbstractTensor, TransformFunction

class Invalid: pass
invalid = Invalid()

class Validator(foundation.Visitor):
	def __init__(self, environment:dict, complain:Callable):
		self.__complain = complain
		self.__type_env = {}
		for k,v in environment.items():
			assert isinstance(k, str) and isinstance(v, AbstractTensor)
			k_prime = k.lower()
			assert k_prime not in self.__type_env, "%r has a case-folded duplicate. That's bad."%k
			v.tt.validate_for_API(k_prime)
			self.__type_env[k_prime] = v.tt
		
	def visit_list(self, items):
		for i in items: self.visit(i)
	
	def visit_DefineTensor(self, dt:frontend.DefineTensor):
		if dt.name.text in self.__type_env:
			self.__complain(*dt.name.span, message="Tensor name was previously defined; ignoring redefinition.")
		else:
			tt = self.visit(dt.expr)
			if tt is invalid: self.__complain(*dt.name.span, message="Tensor value therefore has invalid spatial type.")
			else: print(dt.name.text, 'has shape', sorted(tt.space))
			self.__type_env[dt.name.text] = tt
	
	def __symmetric_types(self, a_exp, op_span, b_exp):
		t_a = self.visit(a_exp)
		t_b = self.visit(b_exp)
		if isinstance(t_a, Invalid): return t_a
		if isinstance(t_b, Invalid): return t_b
		assert isinstance(t_a, TensorType) and isinstance(t_b, TensorType)
		common_context = t_a.context & t_b.context
		if t_a.space == t_b.space:
			return TensorType(t_a.space, common_context)
		elif t_a.e_space == t_b.e_space:
			return TensorType(t_a.e_space-common_context, common_context)
		else:
			diff = set(t_a.e_space).symmetric_difference(t_b.e_space)
			self.__complain(*op_span, message="Operand spaces do not agree about %r"%diff)
			return invalid
	
	def visit_TensorSum(self, d: frontend.TensorSum): return self.__symmetric_types(*d)
	def visit_Difference(self, d: frontend.Difference): return self.__symmetric_types(*d)
	def visit_Product(self, d: frontend.Product): return self.__symmetric_types(*d)
	def visit_Quotient(self, d: frontend.Difference): return self.__symmetric_types(*d)
	
	def visit_Multiplex(self, m:frontend.Multiplex):
		dim = m.criterion.axis
		presume = self.__symmetric_types(m.if_true, dim.span, m.if_false)
		if isinstance(presume, TensorType):
			if dim.text not in presume.space:
				self.__complain(*dim.span, message="Dimension %r is not available here. options are %r."%(dim.text, sorted(presume.space)))
				return invalid
		else:
			assert isinstance(presume, Invalid)
		return presume
		
	
	def visit_Aggregation(self, agg:frontend.Aggregation):
		a_type = self.visit(agg.a_exp)
		if isinstance(a_type, Invalid): return a_type
		new_space = set()
		for dim in agg.new_space:
			if dim.text in new_space:
				self.__complain(*dim.span, message="Dimension was mentioned earlier in the same list.")
				return invalid
			if dim.text not in a_type.space:
				self.__complain(*dim.span, message="Dimension %r is not available here. options are %r."%(dim.text, sorted(a_type.space)))
				return invalid
			new_space.add(dim.text)
		return TensorType(new_space, a_type.context)
	
	def visit_Name(self, n:frontend.Name):
		try: return self.__type_env[n.text]
		except KeyError:
			self.__complain(*n.span, message="undefined name.")
			return invalid
	
	def visit_ScaleBy(self, s:frontend.ScaleBy):
		return self.visit(s.a_exp)

	def visit_SumImage(self, si:frontend.SumImage):
		# Checking type is a bit easier than doing an optimal grouping, because
		# ideally you'd like to compute the transforms in parallel to avoid
		# making multiple passes through the data.
		a_type = self.visit(si.a_exp)
		for mx in si.sums:
			if isinstance(a_type, Invalid): return a_type
			assert isinstance(a_type, TensorType), type(a_type)
			a_type = self.__apply_one_transform(a_type, mx)
		return a_type
	
	def __apply_one_transform(self, a_type:TensorType, mx:frontend.MappingExpression) -> Union[TensorType, Invalid]:
		# First, apply a simple textual test:
		effective_space = set(a_type.e_space)
		for dim in mx.domain:
			try: effective_space.remove(dim.text)
			except KeyError:
				self.__complain(*dim.span, message="Dimension %r is not available here. options are %r." % (dim.text, sorted(effective_space)))
				return invalid
		for dim in mx.range:
			if dim.text in effective_space:
				self.__complain(*dim.span, message="Dimension %r is already present in the input tensor."%dim.text)
				return invalid
			else: effective_space.add(dim.text)
		
		# Next, do we have a registered function in the environment to perform this translation?
		domain = frozenset(dim.text for dim in mx.domain)
		range_ = frozenset(dim.text for dim in mx.range)
		
		# -->> TODO: Save for later.
		
		# Finally, work out the actual transform and apply it in detail to the TensorType object:
		if domain <= a_type.context: # In this case, there's an operational short-cut which ought to be applied.
			context = (a_type.context - domain) | range_
			space = a_type.space
		else:
			context = a_type.context - domain
			space = (a_type.space - domain) | range_
		return TensorType(space, context)


