from setuptools import setup

setup(
    name='token_state_relational_mapper',
    packages=['token_state_relational_mapper'],
    include_package_data=True,
    install_requires=[
        'eth-utils==1.2.2',
        'web3==4.7.2',
        'click',
        'Flask-SQLAlchemy',
        'psycopg2',
        'requests',
        'sqlalchemy',
        'flask==0.12.4',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ]
)
