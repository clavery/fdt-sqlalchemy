#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='fdt-sqlalchemy',
    version='0.0.1',
    description='Flask-debugtoolbar configurable SQLAlchemy panel',
    author='Charles Lavery',
    author_email='charles.lavery@gmail.com',
    url='https://github.com/clavery/fdt-sqlalchemy',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLAlchemy>=0.9.0',
        'Flask-DebugToolbar>=0.9.0',
    ],
    license='BSD',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ),
)
