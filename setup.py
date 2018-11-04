from setuptools import setup

setup(
    name='juleol',
    packages=['juleol'],
    include_package_data=True,
    install_requires=[
        'gunicorn',
        'flask~=1.0',
        'flask-bcrypt',
        'Flask-Dance',
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
