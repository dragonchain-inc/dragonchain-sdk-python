#!/usr/bin/env python3

import os
import re
from setuptools import setup, find_packages


def get_version():
    root = os.path.dirname(os.path.abspath(__file__))
    init = open(os.path.join(root, 'dragonchain_sdk', '__init__.py')).read()
    return re.compile(r'''__version__ = ['"]([0-9.]+)['"]''').search(init).group(1)


setup(
    name='dragonchain_sdk',
    version=get_version(),
    author='Dragonchain',
    author_email='support@dragonchain.com',
    description='Dragonchain SDK for Python',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/dragonchain-inc/dragonchain-sdk-python',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    scripts=[],
    install_requires=[
        'requests'
    ],
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
