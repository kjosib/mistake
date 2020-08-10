"""
Of course a sandbox is much enhanced by the provision of toys.
The better toys may be promoted to proper members of the toolkit.

These toys are meant for experimentation:
	Neither organization nor documentation are assured.
"""

from typing import Dict
import zipfile, re
from mistake import domain

#----------------------------------------------------------------------------------------------------

# There's a big difference between type and storage-class. The former is about theory and semantics.
# The latter is about the concrete organization of data for storage and retrieval with particular
# space and time characteristics.

# Let's posit a simple storage class:

class TensorValue:
	""" This is sort of a default "simplest conceivable" storage class """
	def __init__(self, tt:domain.TensorType, context:Dict[str, object]=()):
		self.tt = tt
		self.context = dict(context)
		assert self.context.keys() == tt.context # Semantic validation should prove this.
		self.__storage = {}
		self.__schedule = tuple(self.tt.space)

	def __key(self, point:dict) -> tuple:
		# We can worry about the VALIDITY of keys later.
		return tuple(point[k] for k in self.__schedule)

	def get(self, point): return self.__storage.get(self.__key(point), 0)

	def set(self, point, value): self.__storage[self.__key(point)] = value
	
	def increment(self, point, value):
		key = self.__key(point)
		self.__storage[key] = self.__storage.get(key, 0) + value
	
	def items(self):
		for key,value in self.__storage.items():
			yield dict(zip(self.__schedule, key)), value

def northwind(table_name, **adjust):
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
			for k,fn in adjust.items(): row[k] = fn(row[k])
			yield row

