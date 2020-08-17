r"""
{-
Ever since reading Jack Crenshaw's series on building a compiler,
it's seemed that "cradle" is as good a name as any for the first
initial "get things moving" module.

As a sample working environment, I'm using the order_details table
from (the enclosed copy of) the Northwind Traders database.

This module has become a
-}

gross is quantity_sold * unit_price -- Operations are are element-wise.
discount is gross * discount_rate   -- Things are computed only if necessary.
net_value is gross - discount   -- Enforce single-assignment: this line errors.
net_value is gross              -- Ignore re-definition: this line also errors.
foo is bar                      -- Cope with undefined names. 'foo' becomes defined but invalid.

average_discount is discount by [ProductID] / quantity_sold by [ProductID]
borken_average is discount by [ProductID] / quantity_sold by [OrderID] -- cope with mismatched dimensions.
missing_dim is average_discount by [product_id]   -- Note the misspelled dimension name.
double_dim is net_value by [ProductID, ProductID]

bar is average_discount / 2

nonsense_1 is net_value where ProductID < 1000 else average_discount -- Catches on the tensor spaces

nonsense_2 is net_value where no_such_thing < 1000 else discount -- Catches a bogus dimension
	-- There really ought to be a way to catch comparing (e.g.) dates with numbers,
	-- but that means a table of available dimensions with their characteristics.

nonsense_3 is net_value where ProductID < 1000 else discount -- This particular atrocity is not yet caught.

-- Now let's suppose I want to know how much revenue I've collected from each country:

revenue_by_country is net_value sum { orderid -> shipcountry } by [shipcountry]

"""

from mistake import frontend, planning
import toys

parser = frontend.Parser()
ast = parser.parse(__doc__)
if ast is not None:
	universe = toys.sample_universe()
	planning.Planner(universe, parser.source.complain).visit(ast)
	for p, v in universe.get_tensor('revenue_by_country').stream():
		print(p, round(v,2))

