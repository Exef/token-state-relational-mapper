from setuptools import setup

setup(
    name='token_state_relational_mapper',
    packages=['token_state_relational_mapper'],
    include_package_data=True,
    install_requires=[
        'eth-utils==0.7.4',
        'web3==3.16.5',
        'click',
        'Flask-SQLAlchemy',
        'psycopg2',
        'requests',
        'sqlalchemy',
        'flask',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ]
)
