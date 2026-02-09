from setuptools import setup, find_packages
import re
from pathlib import Path

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# Read version from __init__.py without importing
def get_version():
    init_file = Path("imprest_management") / "__init__.py"
    content = init_file.read_text()
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "1.0.0"

setup(
    name="imprest_management",
    version=get_version(),
    description="Complete imprest (cash advance) management system for Frappe/ERPNext",
    author="Tagrit",
    author_email="info@tagrit.com",
    packages=find_packages(exclude=["*.workspace", "*.workspace.*"]),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)