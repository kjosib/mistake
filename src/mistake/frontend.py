from typing import NamedTuple, Tuple
from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import utility

TABLES = utility.tables(__file__, 'mistake_grammar.md')

class Name(NamedTuple):
	text:str
	span:Tuple[int,int]

class DefineTensor(NamedTuple):
	name:Name
	expr:object

class Difference(NamedTuple):
	a_exp: object
	span:Tuple[int,int]
	b_exp: object



class CoreDriver(brt.TypicalApplication):
	MONTHS = {m:n for n,m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(),1)}
	RESERVED_WORDS = frozenset('else week where space tensor of is'.split()) | MONTHS.keys()
	
	def __init__(self):
		super(CoreDriver, self).__init__(TABLES)
		self.module = {}
	
	def scan_ignore(self, yy:Scanner, what):
		pass
	
	def scan_enter(self, yy:Scanner, condition):
		yy.enter(condition)
	
	def scan_word(self, yy:Scanner):
		text = yy.matched_text().lower() # By this the language is made caseless.
		if text in self.RESERVED_WORDS:
			if text in self.MONTHS: yy.token('month', self.MONTHS[text])
			else: yy.token(text)
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
	
	parse_define_tensor = staticmethod(DefineTensor)
	parse_difference = staticmethod(Difference)

