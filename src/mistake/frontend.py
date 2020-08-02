from boozetools.support import runtime as brt
from boozetools.support.interfaces import Scanner
from . import utility

TABLES = utility.tables(__file__, 'mistake_grammar.md')

class CoreDriver(brt.TypicalApplication):
	def scan_word(self, yy:Scanner):
		yy.token("ID", yy.matched_text())
		print(yy.matched_text())
