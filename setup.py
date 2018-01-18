from setuptools import setup

setup(
    name='token_state_relational_mapper',
    packages=['token_state_relational_mapper'],
    include_package_data=True,
    install_requires=[
        'flask',
        'web3',
        'click',
        'Flask-SQLAlchemy',
        'psycopg2', 'requests', 'sqlalchemy'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ]
)