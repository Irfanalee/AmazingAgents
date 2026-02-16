"""
Setup configuration for Shadow ARB package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadow-arb",
    version="1.0.0",
    author="Your Organization",
    author_email="engineering@yourorg.com",
    description="AI-Powered Architecture Review Board for automated code reviews",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/shadow-arb",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "langgraph>=0.2.45",
        "langchain-core>=0.3.15",
        "PyGithub>=2.4.0",
        "pydantic>=2.9.2",
        "litellm>=1.52.7",
        "python-dotenv>=1.0.1",
    ],
    extras_require={
        "dev": [
            "mypy>=1.13.0",
            "pytest>=7.4.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shadow-arb=main:main",
        ],
    },
)
