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

-- Now let's suppose I want to know how much revenue I've collected from each country:

revenue_by_country is net_value sum { orderid -> shipcountry }

"""
from mistake import frontend, validation
from mistake.domain import TensorType, Dimension
from toys import ConcreteTensor, northwind

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
	tensor_qty = ConcreteTensor(tt)
	tensor_gross = ConcreteTensor(tt)
	tensor_discount = ConcreteTensor(tt)
	
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
	validation.Validator(sample_environment(), parser.source.complain).visit(ast)

