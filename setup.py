
import setuptools


with open("README.md", "r",encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="autosend",
    version="0.0.4",
    author="flish_wang",
    author_email="flish_wang@sina.com",
    description="a simple tool that logs what is printed on the screen, and emails the logs to you",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/flishwang/autosend",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        "pyyaml",
    ],
    python_requires=">=3"
)

