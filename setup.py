from setuptools import setup, find_packages

setup(
    name="Zero_assignment",
    version="0.1",
    packages=find_packages(),

    # Metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for Zero_assignment project",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pandas",
        "sentence_transformers",
        "numpy",
        'flask',
    ],
)
