from setuptools import setup
import sys

if sys.version_info[0] == 2:
    sys.exit("Sorry, Python 2 is no longer supported. Please use a version of Qhue < 2.0.")

major_version = 2
minor_version = 0
build_version = 1

version = str(major_version) + "." + str(minor_version) + "." + str(build_version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="qhue",
    python_requires='>3.4',
    version=version,
    description="Qhue: python wrapper for Philips Hue API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Quentin Stafford-Fraser",
    url="https://github.com/quentinsf/qhue",
    license="GNU GPL 2",
    packages=("qhue",),
    install_requires=("requests", "requests_oauthlib"),
)
