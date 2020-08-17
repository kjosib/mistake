"""
Of course a sandbox is much enhanced by the provision of toys.
The better toys may be promoted to proper members of the toolkit.

These toys are meant for experimentation:
	Neither organization nor documentation are assured.
"""

from typing import Dict, Generator, Callable
import zipfile, re
from mistake.domain import Universe, Dimension, AbstractTensor, Space


#----------------------------------------------------------------------------------------------------

# There's a big difference between type and storage-class. The former is about theory and semantics.
# The latter is about the concrete organization of data for storage and retrieval with particular
# space and time characteristics.

# Let's posit a simple storage class:


def northwind(table_name):
	"""
	Yield a stream of "records" as dictionaries, with certain adjustments.
	
	So it turns out my source of NorthWind data has a bizarre nonstandard format:
	Embedded commas are those followed by whitespace!
	The usual csv module doesn't handle that by default and neither does MS Excel.
	Fortunately it's not hard to deal with. Anyway, this is just a concept demo.
	It doesn't have to be amazing. It has to get a point across, and the weird CSV
	format is not that point.
	"""
	def split(s:str): return delimiter.split(s.rstrip('\n'))
	delimiter = re.compile(r',(?!\s)')
	with zipfile.ZipFile('northwind.zip', 'r') as archive:
		text = iter(archive.read(table_name+'.csv').decode('utf-8').splitlines())
		heads = [h.lower() for h in split(next(text))]
		for tails in text:
			row = dict(zip(heads, split(tails)))
			yield row

#----------------------------------------------------------------------------------------------------
#
# Let's do something even less sophisticated:

class KissTensor(AbstractTensor):
	def __init__(self, table_name, key_space:Dict[str,Callable[[str],object]], field:str):
		self.__table_name = table_name
		self.__key_space = key_space
		self.__field = field
	def stream(self) -> Generator:
		for row in northwind(self.__table_name):
			point = {k:fn(row[k]) for k,fn in self.__key_space.items()}
			value = float(row[self.__field])
			yield point, value
	
	def space(self) -> Space:
		return frozenset(self.__key_space.keys())


def sample_universe() -> Universe:
	universe = Universe({
		'productid': Dimension(),
		'orderid': Dimension(),
		'shipcountry': Dimension(),
	})
	
	key_space = dict(productid=int, orderid=int)
	universe.register_tensor('quantity_sold', KissTensor('order-details', key_space, 'quantity'))
	universe.register_tensor('unit_price', KissTensor('order-details', key_space, 'unitprice'))
	universe.register_tensor('discount_rate', KissTensor('order-details', key_space, 'discount'))
	
	orders = {int(row['orderid']):row for row in northwind('orders')}
	
	universe.register_attribute('orderid', 'shipcountry', lambda oid:orders[oid]['shipcountry'])
	
	return universe
	
