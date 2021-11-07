# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools.command.test import test as TestCommand

setup(
    name="juleol",
    packages=["juleol"],
    include_package_data=True,
    install_requires=[
        "blinker",
        "idna==2.7",
        "gunicorn",
        "flask~=2.0",
        "Flask-Dance~=5.0",
        "flask_migrate",
        "flask_login",
        "Flask-Sessionstore",
        "flask_sqlalchemy",
        "PyMySQL",
        "wtforms[email]",
        "SQLAlchemy~=1.4.23",
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "betamax",
        "betamax_serializers",
        "coverage",
        "pytest",
        "pytest-cov",
    ],
)
