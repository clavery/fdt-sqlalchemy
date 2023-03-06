#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='fdt-sqlalchemy',
    version='0.0.5',
    description='Flask-debugtoolbar configurable SQLAlchemy panel',
    author='Charles Lavery & Davide Marchi',
    author_email='charles.lavery@gmail.com',
    url='https://github.com/clavery/fdt-sqlalchemy',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy>=2.0.4',
        'Flask-DebugToolbar>=0.13.1',
    ],
    license='BSD',
    zip_safe=False,
    provides=[],
    classifiers=(
    ),
)
