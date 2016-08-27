from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='sq100',
    version="0.0.1",
    url='http://github.com/tnachstedt/sq100/',
    license='Apache Software License',
    author='Timo Nachstedt',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={'test': PyTest},
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