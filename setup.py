from setuptools import setup, find_packages

import os.path


def get_requirements(env):
    with open("requirements-{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


root = os.path.dirname(__file__)

setup(
    name="gitboard",
    version="0.1.0",
    description="",
    author="David Cramer",
    url="https://github.com/dcramer/gitboard",
    entry_points={"console_scripts": ["gitboard=gitboard.cli:main"]},
    install_requires=get_requirements("base"),
    packages=find_packages(),
    include_package_data=True,
)
