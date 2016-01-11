from setuptools import find_packages
from setuptools import setup

install_requires = [
    'numpy',
    ]

tests_require = [
    'pytest',
    ]

setup(name='PyAudioGraph',
    version='0.1',
    description='Python Audio Graph',
    author='Bruno Di Giorgi',
    author_email='massimiliano.zanoni@polimi.it',
    url='https://github.com/brunodigiorgi/pyAudioGraph',
    license="GPLv2",
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
       	'testing': tests_require,
       	},
    )