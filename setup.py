from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in afif/__init__.py
from afif import __version__ as version

setup(
	name="afif",
	version=version,
	description="Afif",
	author="Akwad",
	author_email="support@akwad.qa",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
