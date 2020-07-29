import pathlib, tempfile, pickle, os
from typing import Callable

def pickle_cache(source_path, cache_path, method:Callable):
	"""
	Generically, suppose some input-file changes only rarely but you apply a complex
	computation to that file to produce a working data structure. You'd like to check
	a couple timestamps rather than rebuild a complete parsing automaton every time,
	for example.
	
	:param source_path: The path to the input file
	:param cache_path: The path to the cache pickle.
	:param method: (computationally-intensive) function from source-path to result.
	:return: whatever method(source_path) does, but only recomputed when source_path changes.
	"""
	
	def rebuild():
		result = method(source_path)
		with open(cache_path, 'wb') as ofh:
			pickle.dump((src_stat.st_mtime, src_stat.st_size, result), ofh)
		return result
	
	src_stat = os.stat(source_path)
	try: cache_stat = os.stat(cache_path)
	except FileNotFoundError: return rebuild()
	if src_stat.st_mtime > cache_stat.st_mtime: return rebuild()
	try:
		with open(cache_path, 'rb') as ifh:
			saved_mtime, saved_size, saved_result = pickle.load(ifh)
	except: return rebuild()
	if (saved_mtime, saved_size) == (src_stat.st_mtime, src_stat.st_size): return saved_result
	else: return rebuild()


def tables(basis, doc) -> dict:
	"""
	Perhaps this routine belies a deficiency in the stack, but the object is to be able to
	compile the grammar only once (or whenever it changes) and use it over and over.
	In a fully-packaged solution a pre-pickled table may seem desirable, but for now
	this adaptive approach is better for hacking on.
	"""
	source_path = pathlib.Path(basis).parent/doc
	cache_path = pathlib.Path(tempfile.gettempdir())/(doc+'.pickle')
	def method():
		from boozetools.macroparse import compiler
		return compiler.compile_file(source_path, method='LR1')
	
	return pickle_cache(source_path, cache_path, method)
