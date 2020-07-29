"""
Packaging script for PyPI.
"""

import setuptools

exec(open('src/mistake/version.py').read())

setuptools.setup(
	name='mistake',
	author='Ian Kjos',
	author_email='kjosib@gmail.com',
	version=__version__,
	packages=['mistake', ],
	package_dir = {'': 'src'},
	package_data={
		'mistake': ['mistake_grammar.md',],
	},
	license='MIT',
	description='a language for not losing your marbles around high-dimensional matrices',
	long_description=open('README.md').read(),
	long_description_content_type="text/markdown",
	url="https://github.com/kjosib/mistake",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Topic :: Office/Business",
		"Topic :: Software Development :: Interpreters",
		"Topic :: Software Development :: Libraries",
		
    ],
	python_requires='>=3.7',
	install_requires=[
		'booze-tools>=0.4.3',
	]
)