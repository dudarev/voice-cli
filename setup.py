from pkg_resources import parse_requirements
from setuptools import setup

with open("requirements.txt") as f:
    requirements = [str(req) for req in parse_requirements(f)]

setup(
    name="voice-cli",
    version="0.0.5",
    py_modules=["main"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "v = main:cli",
        ],
    },
)
