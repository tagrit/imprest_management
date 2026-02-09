from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

from imprest_management import __version__ as version

setup(
    name="imprest_management",
    version=version,
    description="Complete imprest (cash advance) management system for Frappe/ERPNext",
    author="Tagrit",
    author_email="info@tagrit.com",
    packages=find_packages(exclude=["*.workspace", "*.workspace.*"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
