import io
import os
from setuptools import find_packages, setup

EXCLUDE_FROM_PACKAGES = ["contrib", "docs", "tests*"]
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()


setup(
    name="starlette-auth-toolkit",
    version="0.1.0",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description=(
        "Authentication backends and helpers for "
        "Starlette-based apps and frameworks"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/florimondmanca/starlette-auth-toolkit.git",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    python_requires=">=3.6",
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: MIT License",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
