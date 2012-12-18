#!/usr/bin/env python
# encoding: utf8
# The COPYRIGHT file at the top level of this repository contains the full 
# copyright notices and license terms.

from setuptools import setup, find_packages
import os

execfile(os.path.join('pypi_client', 'version.py'))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name=PACKAGE,
    version=VERSION,
    description='pypi_client',
    long_description=read('README'),
    author='Guillem Barba',
    author_email='guillem@nan-tic.com',
    url=WEBSITE,
    download_url="http://www.nan-tic.com/" + \
            VERSION.rsplit('.', 1)[0] + '/',
    packages=find_packages(),
    package_data={},
    scripts=[],
    classifiers=[
#        'Development Status :: 5 - Production/Stable',
#        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ],
    license=LICENSE,
    install_requires=[
        'jsonpickle',
        ],
    extras_require={},
    zip_safe=False,
    test_suite='',
)
