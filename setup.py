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
        'flask-bcrypt',
        'Flask-Dance~=3.0',
        'flask_migrate',
        'flask_sqlalchemy',
        'PyMySQL',
        'wtforms',
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "coverage",
        "pytest",
        "pytest-cov",
    ],
)
