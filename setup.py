import re
import ast
import setuptools


_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("dmdevtools/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
    long_description_content_type = "text/markdown"

setuptools.setup(
    name="digitalmarketplace-developer-tools",
    version=version,
    url="https://github.com/alphagov/digitalmarketplace-developer-tools",
    license="MIT",
    author="GDS Developers",
    description="Common developer tools for Digital Marketplace repos",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    packages=setuptools.find_packages(),
    python_requires="~=3.6",
    install_requires=[
        "invoke",
    ],
)
