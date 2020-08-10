r"""
{-
Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.

As a sample working environment, I'm using the order_details table
from (the enclosed copy of) the Northwind Traders database.
-}

net_value is gross - discount   -- Let's say we do single-assignment form.
net_value is gross              -- Ignore re-definition.
foo is bar                      -- Cope with undefined names. 'foo' becomes defined but invalid.

average_discount is discount by [ProductID] / quantity_sold by [ProductID]
borken_average is discount by [ProductID] / quantity_sold by [OrderID] -- cope with mismatched dimensions.
missing_dim is average_discount by [product_id]
double_dim is net_value by [ProductID, ProductID]

bar is average_discount / 2

nonsense_1 is net_value where ProductID < 1000 else average_discount -- Catches on the tensor spaces

nonsense_2 is net_value where no_such_thing < 1000 else discount -- Catches a bogus dimension
	-- There really ought to be a way to catch comparing (e.g.) dates with numbers,
	-- but that means a table of available dimensions with their characteristics.

nonsense_3 is net_value where ProductID < 1000 else discount -- This particular atrocity is not yet caught.

"""
from typing import Callable
from boozetools.support import foundation
from mistake import frontend
from mistake.domain import TensorType, Dimension
from toys import TensorValue, northwind

class Invalid: pass
invalid = Invalid()

class Validator(foundation.Visitor):
	def __init__(self, environment:dict, complain:Callable):
		self.__complain = complain
		self.__type_env = {}
		for k,v in environment.items():
			assert isinstance(k, str) and isinstance(v, TensorValue)
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
			else: print(dt.name.text, 'has shape', sorted(tt.space.keys()))
			self.__type_env[dt.name.text] = tt
	
	def __symmetric_types(self, a_exp, op_span, b_exp):
		t_a = self.visit(a_exp)
		t_b = self.visit(b_exp)
		if isinstance(t_a, Invalid): return t_a
		if isinstance(t_b, Invalid): return t_b
		assert isinstance(t_a, TensorType) and isinstance(t_b, TensorType)
		if t_a.space == t_b.space:
			return TensorType(t_a.space, t_a.context & t_b.context)
		else:
			diff = set(t_a.space).symmetric_difference(t_b.space)
			self.__complain(*op_span, message="Operand spaces do not agree about %r"%diff)
			return invalid
	
	def visit_Sum(self, d: frontend.Sum): return self.__symmetric_types(*d)
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
		t_a = self.visit(agg.a_exp)
		if isinstance(t_a, Invalid): return t_a
		new_space = {}
		for dim in agg.new_space:
			if dim.text in new_space:
				self.__complain(*dim.span, message="Dimension was mentioned earlier in the same list.")
				return invalid
			if dim.text not in t_a.space:
				self.__complain(*dim.span, message="Dimension %r is not available here. options are %r."%(dim.text, sorted(t_a.space)))
				return invalid
			new_space[dim.text] = t_a.space[dim.text]
		return TensorType(new_space, t_a.context)
	
	def visit_Name(self, n:frontend.Name):
		try: return self.__type_env[n.text]
		except KeyError:
			self.__complain(*n.span, message="undefined name.")
			return invalid
	
	def visit_ScaleBy(self, s:frontend.ScaleBy):
		return self.visit(s.a_exp)

# ----------------------------------------------------------------------------------------------------

# Presumably we need to configure some pre-loads into the semantic environment before running
# our little program.

# ----------------------------------------------------------------------------------------------------

# Let's have a go at loading some data:
def sample_environment():
	tt = TensorType({
		'productid': Dimension(),
		'orderid': Dimension(),
	})
	tensor_qty = TensorValue(tt)
	tensor_gross = TensorValue(tt)
	tensor_discount = TensorValue(tt)
	
	for record in northwind('order-details', productid=int, orderid=int, quantity=int, unitprice=float, discount=float):
		qty = record['quantity']
		price = record['unitprice'] * qty
		discount = price * record['discount']
		tensor_qty.increment(record, qty)
		tensor_gross.increment(record, price)
		tensor_discount.increment(record, discount)
	
	return {'quantity_sold':tensor_qty, 'gross':tensor_gross, 'discount':tensor_discount}

parser = frontend.Parser()
ast = parser.parse(__doc__)
if ast is not None:
	Validator(sample_environment(), parser.source.complain).visit(ast)

