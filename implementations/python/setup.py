from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="universal-connector-block",
    version="0.1.0",
    author="Universal Integration Protocol Team",
    author_email="team@uip.org",
    description="Python implementation of the Universal Connector Block for the Universal Integration Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/uip-project/python-ucb",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
            "tox>=3.24.0",
            "responses>=0.13.0",
        ],
        "flask": ["flask>=2.0.0"],
        "fastapi": ["fastapi>=0.68.0", "uvicorn>=0.15.0"],
        "django": ["django>=3.2.0"],
        "security": ["cryptography>=35.0.0"],
    },
)
