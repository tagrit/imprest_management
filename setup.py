from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in imprest_management/__init__.py
from imprest_management import __version__ as version

setup(
    name="imprest_management",
    version=version,
    description="Complete imprest (cash advance) management system for Frappe/ERPNext",
    author="Your Company",
    author_email="info@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
