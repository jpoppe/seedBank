#!/usr/bin/env python

from distutils.core import setup
import fnmatch
import os

def get_data_files(dir):
    result = []
    for root, _, files in os.walk(dir):
        files = [os.path.join(root, file) for file in files
                    if not fnmatch.fnmatch(file, '*.pyc')]
        result.append(('/' + root, files))
    return result

def get_scripts(dir):
    return [os.path.join(dir, filename) for filename in os.listdir(dir)]

def get_docs(dir):
    result = []
    for root, _, files in os.walk(dir):
        files = [os.path.join(root, file) for file in files]
        result.append(('/usr/share/doc/seedbank/' + root, files))
    return result

long_description = '''
seedBank is a simple and flexible tool to manage unattended Debian and Ubuntu netboot installations. It is based on Debian preseed files, so it will provide the cleanest Debian installations possible by just using the standard Debian tools. Since version 2.0.0 it also has support for modifying installer ISOs so you could generate ISO's which are able to do unattended installations.
'''

setup(
    name='seedbank',
    version='2.0.0rc7',
    description='The cleanest way of Debian/Ubuntu netboot installations',
    author='Jasper Poppe',
    author_email='jgpoppe@gmail.com',
    maintainer ='Jasper Poppe',
    maintainer_email='jgpoppe@gmail.com',
    url='http://www.infrastructureanywhere.com',
    packages=['seedbank'],
    scripts=get_scripts('bin'),
    data_files = get_data_files('etc') + get_docs('manual') + ['README.rst'],
    requires = 'yaml',
    license='GPL',
    platforms='UNIX',
    long_description=long_description.strip(),
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console'
            'Intended Audience :: Advanced End Users',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Unattended Installations',
            'Topic :: Provisioning',
            'Topic :: Debian Seeding'
    ]
)
