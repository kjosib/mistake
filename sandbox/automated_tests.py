"""
It is a deep irony that test-driven development is the only way I'll be able to
keep my wits about developing this package...
"""
import unittest

from mistake import frontend, planning, domain
import toys


class SmokeTest(unittest.TestCase):
	""" When you turn it on, does smoke come out? """
	
	def case(self, expect_count:int, text:str) -> domain.Universe:
		"""
		The general idea is to throw some (grammatically-correct) stuff at the system and
		expect a particular number of "complain" calls. We buffer the messages and compare
		them to the number; if they differ then we emit them all at once and assert False
		to help the developer (that's me) figure out what assumption is breaking. If they
		are the same, then return the universe so the test case can make further checks.
		"""
		def note_complaint(index,width,message): actual.append((index,width,message))
		def emit_saved_complaints():
			for index,width,message in actual:
				parser.source.complain(index,width,message=message)
		actual = []
		parser = frontend.Parser()
		ast = parser.parse(text)
		assert ast is not None
		universe = toys.sample_universe()
		planning.Planner(universe, note_complaint).visit(ast)
		if len(actual) == expect_count:
			return universe
		else:
			emit_saved_complaints()
			assert False
	
	def test_smoke(self):
		# It should at least do sensible things...
		universe = self.case(0, """
			gross is quantity_sold * unit_price
			discount is gross * discount_rate
			net_value is gross - discount
			average_discount is discount by [ProductID] / quantity_sold by [ProductID]
			bar is average_discount / 2
		""")
		for t, s in {
			'quantity_sold' : {'orderid', 'productid'},
			'unit_price' : {'orderid', 'productid'},
			'gross' : {'orderid', 'productid'},
			'net_value' : {'orderid', 'productid'},
			'average_discount' : {'productid'},
			'bar' : {'productid'},
		}.items():
			with self.subTest(t):
				self.assertEqual(s, universe.get_tensor(t).space())
	
	def test_undefined_name(self):
		# Note that using an undefined name causes a secondary complaint, which is
		# the location of the name that now has invalid type.
		self.case(2, "gross is some_undefined_name * unit_price")

	def test_redefined_name(self):
		self.case(1, """
			gross is quantity_sold * unit_price
			gross is quantity_sold
		""")
	

		
if __name__ == "__main__":
	unittest.main()
