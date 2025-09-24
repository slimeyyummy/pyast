from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyast",
    version="0.1.0",
    author="PyAST Contributors",
    author_email="",
    description="A powerful Python AST implementation with advanced features for code analysis and transformation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slimeyyummy/pyast-remake/tree/main",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "coverage",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyast=pyast.main:main",
        ],
    },
    keywords="python ast parser transformer compiler analysis",
    project_urls={
        "Source": "https://github.com/slimeyyummy/pyast-remake/tree/main",
    },
    include_package_data=True,
    zip_safe=False,
)
