
from setuptools import setup, find_packages

setup(
	name='panoptes',
	version=__import__('panoptes').__version__,
	description='A usage-tracking tool designed for computer labs.',
	author='Justin Locsei',
	author_email='justin.locsei@oberlin.edu',
	url='https://github.com/cilcoberlin/panoptes',
	download_url='https://github.com/cilcoberlin/panoptes/zipball/master',
	packages=find_packages(),
	package_data={'': ["*.*"]},
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Framework :: Django'
	]
)
