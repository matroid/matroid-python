import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'matroid'))
from version import VERSION

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(
    name='matroid',
    version=VERSION,
    description='Matroid API Python Library',
    author='Matroid',
    author_email='support@matroid.com',
    url='https://github.com/matroid/matroid-python',
    install_requires=['requests'],
    packages=['matroid'],
    use_2to3=True
)
