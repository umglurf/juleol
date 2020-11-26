# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools.command.test import test as TestCommand

setup(
    name='juleol',
    packages=['juleol'],
    include_package_data=True,
    install_requires=[
        'idna==2.7',
        'gunicorn',
        'flask~=1.0',
        'Flask-Dance~=3.0',
        'flask_migrate',
        'flask_sqlalchemy',
        'PyMySQL',
        'wtforms[email]',
        'SQLAlchemy~=1.3.20',
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        'betamax',
        "coverage",
        "pytest",
        "pytest-cov",
    ],
)
