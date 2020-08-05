from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import utility

TABLES = utility.tables(__file__, 'mistake_grammar.md')

class CoreDriver(brt.TypicalApplication):
	MONTHS = {m:n for n,m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(),1)}
	RESERVED_WORDS = frozenset('else week where'.split()) | MONTHS.keys()
	
	def scan_ignore(self, yy:Scanner, what):
		pass
	
	def scan_enter(self, yy:Scanner, condition):
		yy.enter(condition)
	
	def scan_word(self, yy:Scanner):
		text = yy.matched_text().lower() # By this the language is made caseless.
		if text in self.RESERVED_WORDS:
			if text in self.MONTHS: yy.token('month', self.MONTHS[text])
			else: yy.token(text)
		else: yy.token("id", text)
	
	def scan_relop(self, yy:Scanner, which):
		yy.token('relop', which)
	
	def scan_integer(self, yy:Scanner):
		yy.token('integer', int(yy.matched_text()))
		
	def scan_real(self, yy:Scanner):
		yy.token('real', float(yy.matched_text()))
		
