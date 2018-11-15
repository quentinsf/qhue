from setuptools import setup

major_version = 1
minor_version = 0
build_version = 10

version = str(major_version) + '.' + str(minor_version) + '.' + str(build_version)

setup(
    name='qhue',
    version=version,
    description='Qhue: python wrapper for Philips Hue API',
    author='Quentin Stafford-Fraser',
    url='https://github.com/quentinsf/qhue',
    license='GNU GPL 2',
    packages=('qhue',),
    install_requires=('requests',),
)
