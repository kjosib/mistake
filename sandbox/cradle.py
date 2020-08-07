r"""
{-
Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.
-}

net_value is gross - discount   -- Let's say we do single-assignment form.
net_value is gross              -- Ignore re-definition.
foo is bar                      -- Cope with undefined names.

"""

from boozetools.support import foundation
from mistake import frontend
from toys import TensorType, TensorValue

class Incorrect: pass
incorrect = Incorrect()

class Validator(foundation.Visitor):
	def __init__(self, environment:dict):
		self.__type_env = {}
		for k,v in environment.items():
			assert isinstance(k, str) and isinstance(v, TensorValue)
			self.__type_env[k] = v.tt
		
	def visit_list(self, items):
		for i in items: self.visit(i)
	
	def visit_DefineTensor(self, dt:frontend.DefineTensor):
		if dt.name.text in self.__type_env:
			parser.source.complain(*dt.name.span, message="name was previously defined; ignoring redefinition.")
		else:
			tt = self.visit(dt.expr)
			if tt is incorrect: parser.source.complain(*dt.name.span, message="unable to infer correct spatial type.")
			else: print(dt.name.text, 'has shape', sorted(tt.space.keys()))
			self.__type_env[dt.name.text] = tt
	
	def visit_Difference(self, d:frontend.Difference):
		t_a = self.visit(d.a_exp)
		t_b = self.visit(d.b_exp)
		if incorrect in (t_a, t_b): return incorrect
		assert isinstance(t_a, TensorType) and isinstance(t_b, TensorType)
		if t_a.space == t_b.space:
			return TensorType(t_a.space, t_a.context & t_b.context)
		else:
			diff = set(t_a.space).symmetric_difference(t_b.space)
			parser.source.complain(*d.span, message="operand spaces do not agree about %r"%diff)
			return incorrect
	
	def visit_Name(self, n:frontend.Name):
		try: return self.__type_env[n.text]
		except KeyError:
			parser.source.complain(*n.span, message="undefined name.")
			return incorrect

# ----------------------------------------------------------------------------------------------------

# Presumably we need to configure some pre-loads into the semantic environment before running
# our little program.

# ----------------------------------------------------------------------------------------------------

# Let's have a go at loading some data:
def sample_environment():
	import zipfile, csv
	tt = TensorType({
		'ProductID': '-',
		'OrderID': '-',
	})
	tensor_gross = TensorValue(tt)
	tensor_discount = TensorValue(tt)
	
	northwind = zipfile.ZipFile('northwind.zip', 'r')
	for record in csv.DictReader(northwind.read('order-details.csv').decode('utf-8').splitlines()):
		point = {'ProductID': int(record['ProductID']), 'OrderID': int(record['OrderID']), }
		price = float(record['UnitPrice']) * int(record['Quantity'])
		discount = price * float(record['Discount'])
		tensor_gross.increment(point, price)
		tensor_discount.increment(point, discount)
	
	return {'gross':tensor_gross, 'discount':tensor_discount}

parser = frontend.CoreDriver()
ast = parser.parse(__doc__)
if ast is not None:
	Validator(sample_environment()).visit(ast)

