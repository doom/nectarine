import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    dependencies = list(map(lambda line: line.strip(), f.readlines()))

with open("requirements-yaml.txt", "r") as f:
    yaml_dependencies = list(map(lambda line: line.strip(), f.readlines()))

setuptools.setup(
    name="nectarine",
    version="1.0.4",
    author="Clément Doumergue",
    author_email="clement.doumergue@etna.io",
    description="Library to load configuration from various sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doom/nectarine",
    packages=setuptools.find_namespace_packages(),
    install_requires=dependencies,
    extras_require={
        "yaml": yaml_dependencies,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
