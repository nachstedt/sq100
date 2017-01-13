from __future__ import print_function
from setuptools import setup, find_packages
import io
import codecs
import os
import sys


setup(
    name='sq100',
    version="0.0.1",
    url='http://github.com/tnachstedt/sq100/',
    license='Apache Software License',
    author='Timo Nachstedt',
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    install_requires=[],
    cmdclass={'test': pytest},
    author_email='mail@nachstedt.com',
    description='Alternative read out for the SQ 100 heart rate monitor',
    long_description="""
      Alternative read out for the SQ 100 heart rate monitor
    """,
    packages=['sq100'],
    include_package_data=True,
    platforms='any',
    test_suite='sq100.test.test_sq100',
    scripts=['sq100/gh600_console.py'],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
