from pathlib import Path

from setuptools import find_packages, setup

with open(str(Path(".") / "README.md"), encoding="utf-8") as f:
    README = f.read()

PASSWORDS_REQUIREMENTS = ["passlib>=1.7, <2"]

setup(
    name="starlette-auth-toolkit",
    version="0.5.0",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description=(
        "Authentication backends and helpers for "
        "Starlette-based ASGI apps and frameworks"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/florimondmanca/starlette-auth-toolkit.git",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["starlette >= 0.11"],
    extras_require={
        "passwords": PASSWORDS_REQUIREMENTS,
        "dev": [
            # Tests
            "pytest",
            "pytest-asyncio",
            # Test client
            "requests",
            # Web server
            "uvicorn",
            # Optional password backends
            "argon2-cffi",
            "bcrypt",
            # orm integration
            "orm",
            "databases[sqlite]",
            # Code style
            "black",
            "pylint",
            # Release
            "bumpversion",
        ],
    },
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
