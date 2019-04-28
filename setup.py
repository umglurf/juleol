from setuptools import setup

setup(
    name='juleol',
    packages=['juleol'],
    include_package_data=True,
    install_requires=[
        'idna==2.7',
        'gunicorn',
        'flask~=1.0',
        'flask-bcrypt',
        'Flask-Dance~=1.0',
        'flask_sqlalchemy',
        'PyMySQL',
        'wtforms',
    ],
    extras_require={
        'test': [
            'pytest'
        ]
    },
)
