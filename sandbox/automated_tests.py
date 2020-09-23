"""
It is a deep irony that test-driven development is the only way I'll be able to
keep my wits about developing this package...
"""
import unittest

from mistake import frontend, planning, semantics
import toys


class SmokeTest(unittest.TestCase):
	""" When you turn it on, does smoke come out? """
	
	def case(self, expect_count:int, text:str) -> planning.MistakeModule:
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
		universe = toys.sample_module()
		planning.Planner(universe, note_complaint).visit(ast)
		if len(actual) == expect_count:
			return universe
		else:
			emit_saved_complaints()
			self.assertEqual(expect_count, len(actual))
	
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
				self.assertEqual(s, universe.get_tensor(t).tensor_type().space)
	
	def test_undefined_name(self):
		# Note that using an undefined name causes a secondary complaint, which is
		# the location of the name that now has invalid type.
		self.case(2, "gross is some_undefined_name * unit_price")

	def test_redefined_name(self):
		self.case(1, """
			gross is quantity_sold * unit_price
			gross is quantity_sold
		""")
	
	def test_compare_equal_to_environmental_scalar(self):
		# Admittedly this is rather specific to the northwind data...
		universe = self.case(0, """
			something is (quantity_sold * unit_price) where orderid = $some_variable
		""")
		self.assertEqual(2, len(list(universe.query('something', some_variable=10256).content())))
	
	def test_enforce_single_assignment(self):
		self.case(1, """
			gross is quantity_sold * unit_price -- First assignment.
			gross is quantity_sold * unit_price -- Second assignment should error, even if identical.
		""")
	
	def test_refer_to_undefined_name(self):
		self.case(2, """ foo is bar  -- 'foo' becomes defined but invalid. \n""")

	def test_refer_to_invalid_name(self):
		self.case(4, """
			foo is bar  -- 'foo' becomes defined but invalid.
			baz is foo  -- 'foo' is defined but invalid; baz is now also.
		""")
	
	def test_reject_bogus_dimension_name(self):
		self.case(2, """
			invalid is quantity_sold by [bogus_dimension]
		""")
	
	def test_symetric_operation_needs_symetric_arguments(self):
		self.case(2, """
			gross is quantity_sold * unit_price
			discount is gross * discount_rate
			broken_average is discount by [ProductID] / quantity_sold by [OrderID] -- rejects mismatched dimensions.
		""")
	
	def test_reject_double_dimensions(self):
		self.case(2, """
			double_dim is quantity_sold by [ProductID, ProductID] -- reject repeated dimension in target space.
		""")


class TestSemantics(unittest.TestCase):
	"""
	Don't get hung up on the class name. It's a start.
	
	We need to be able to:
		Make one or more of each kind of "type".
		Perform various type-level comparisons, compositions, and promotions (correctly).
			* Dimensional Symmetry
			* Dimensional subset/superset
			* Check that dropped dimensions may be summed over (or perhaps subjected to other ideas?)
			* Check that a particular set of dimensions is valid (e.g. children have their parents along for the ride.)
			* Check that types are add-compatible (i.e. same unit-of-measure, lost dimensions incremental, etc.)
			* Compute the unit-of-measure for some product or quotient
		Analyze a "type" for characteristics.
		Ideally also be able to print out a "type" expression.
	
	These tests are all at the Python level independent of the syntax-directed translation.
	"""
	
	def test_make_a_type(self):
		universe = semantics.UniverseOfDiscourse()
		universe.create_fundamental_unit('each')
		
		foo = semantics.TensorType(['store', 'product', 'customer'], universe['each'])
		assert isinstance(foo, semantics.TensorType)
		foo.require_perfect_symmetry(foo)
		
		bar = semantics.TensorType(['store', 'product', 'salesman'], universe['each'])
		try: foo.require_perfect_symmetry(bar)
		except semantics.Invalid: pass
		else: assert False
	
	def test_play_with_units(self):
		universe = semantics.UniverseOfDiscourse()
		distance = universe.create_fundamental_unit('meter')
		time = universe.create_fundamental_unit('second')
		mass = universe.create_fundamental_unit('kilogram')
		
		velocity = distance / time
		acceleration = velocity / time
		force = mass * acceleration
		
		self.assertEqual('kilogram meter/second^2', str(force))
		self.assertNotEqual(velocity,acceleration)
		
		# While we're at it, prove that care is still required
		work = force * distance
		torque = distance * force
		self.assertEqual(str(work), str(torque))
		self.assertEqual(work, torque)
		
		# Identical (ratio-scale) units should add (and subtract) to themselves:
		self.assertEqual(work, work + torque)
		self.assertEqual(work, work - torque)
		
		# Non-homogenous units should throw an exception if such is attempted:
		try: force + acceleration
		except semantics.Invalid: pass
		else: assert False


if __name__ == "__main__":
	unittest.main()
