#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['Click==7.1.2', 'google-cloud-storage==1.42.2']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="David Su",
    author_email='contact@davidsushi.com',
    python_requires='>=2.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Pip Install Packages Stored in Google Cloud Buckets",
    entry_points={
        'console_scripts': [
            'gs_pip_install=gs_pip_install.gs_pip_install:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='gs_pip_install',
    name='gs_pip_install',
    packages=find_packages(include=['gs_pip_install', 'gs_pip_install.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lucidsushi/gs_pip_install',
    version='0.2.6',
    zip_safe=False,
)
