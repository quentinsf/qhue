from setuptools import setup

major_version = 1
minor_version = 0
build_version = 12

version = str(major_version) + '.' + str(minor_version) + '.' + str(build_version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='qhue',
    version=version,
    description='Qhue: python wrapper for Philips Hue API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Quentin Stafford-Fraser',
    url='https://github.com/quentinsf/qhue',
    license='GNU GPL 2',
    packages=('qhue',),
    install_requires=('requests',),
)
