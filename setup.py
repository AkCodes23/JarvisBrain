"""
Setup script for Jarvis AI Assistant.
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith('#')
    ]

# Read README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Get version from environment variable or default
version = os.getenv('JARVIS_VERSION', '1.0.0')

setup(
    name="jarvis",
    version=version,
    description="A modular AI assistant system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/jarvis",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
            'jarvis=jarvis.core.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/jarvis/issues",
        "Source": "https://github.com/yourusername/jarvis",
        "Documentation": "https://github.com/yourusername/jarvis/docs",
    },
) 