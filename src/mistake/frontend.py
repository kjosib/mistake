from typing import NamedTuple, Tuple, List, Optional
from numbers import Number
from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import utility

Span = Tuple[int,int]

TABLES = utility.tables(__file__, 'mistake_grammar.md')

class Name(NamedTuple):
	text: str
	span: Span

class DefineTensor(NamedTuple):
	name: Name
	expr:object

class TensorSum(NamedTuple):
	a_exp: object
	span: Span
	b_exp: object

class Difference(NamedTuple):
	a_exp: object
	span: Span
	b_exp: object

class Product(NamedTuple):
	a_exp: object
	span: Span
	b_exp: object

class Quotient(NamedTuple):
	a_exp: object
	span: Span
	b_exp: object

class ScaleBy(NamedTuple):
	a_exp: object
	factor: Number

class Aggregation(NamedTuple):
	""" An aggregation is meant to sum over all un-mentioned dimensions. It assumes they may be summed over. """
	a_exp: object
	keyword_span: Span
	new_space:List[Name]

class Criterion(NamedTuple):
	axis: Name
	relop: str
	scalar: object

class Multiplex(NamedTuple):
	if_true: object
	criterion: Criterion
	if_false: object

class MappingExpression(NamedTuple):
	domain: List[Name]
	op_span: Span
	range: List[Name]

class SumImage(NamedTuple):
	a_exp: object
	sums: List[MappingExpression]
	by_span:Optional[Span] = None
	space: Optional[List[Name]] = None

class Parser(brt.TypicalApplication):
	MONTHS = {m:n for n,m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(),1)}
	RESERVED_WORDS = frozenset('else week where space tensor of is by sum'.split()) | MONTHS.keys()
	
	def __init__(self):
		super(Parser, self).__init__(TABLES)
		self.module = {}
	
	def scan_ignore(self, yy:Scanner, what):
		pass
	
	def scan_enter(self, yy:Scanner, condition):
		yy.enter(condition)
	
	def scan_word(self, yy:Scanner):
		text = yy.matched_text().lower() # By this the language is made caseless.
		if text in self.RESERVED_WORDS:
			if text in self.MONTHS: yy.token('month', self.MONTHS[text])
			else: yy.token(text, yy.current_span()) # Sometimes the location of a keyword is used for error reporting.
		else: yy.token("id", Name(text, yy.current_span()))
	
	def scan_relop(self, yy:Scanner, which):
		yy.token('relop', which)
	
	def scan_integer(self, yy:Scanner):
		yy.token('integer', int(yy.matched_text()))
		
	def scan_real(self, yy:Scanner):
		yy.token('real', float(yy.matched_text()))
	
	def scan_punctuation(self, yy: Scanner):
		yy.token(yy.matched_text(), yy.current_span())

	def scan_token(self, yy:Scanner, kind:str):
		yy.token(kind)
	
	def parse_first(self, stmt): return self.parse_subsequent([], stmt)
	def parse_subsequent(self, module, stmt):
		if stmt: module.append(stmt)
		return module
	
	def parse_empty_statement(self):
		pass
	
	parse_empty = staticmethod(list)
	def parse_one(self, item): return [item]
	def parse_more(self, them, item):
		them.append(item)
		return them
	
	parse_define_tensor = staticmethod(DefineTensor)
	parse_tensor_sum = staticmethod(TensorSum)
	parse_difference = staticmethod(Difference)
	parse_product = staticmethod(Product)
	parse_quotient = staticmethod(Quotient)
	
	parse_criterion = staticmethod(Criterion)
	parse_multiplex = staticmethod(Multiplex)
	parse_mapping = staticmethod(MappingExpression)
	parse_sum_image = staticmethod(SumImage)
	parse_sum_image_onto = staticmethod(SumImage)
	
	@staticmethod
	def parse_scale_by(t_exp, _, factor):
		return ScaleBy(t_exp, factor)
	
	@staticmethod
	def parse_scale_divide(t_exp, _, denominator):
		return ScaleBy(t_exp, 1.0/denominator)
	
	parse_aggregate_by = staticmethod(Aggregation)
	
