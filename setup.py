from setuptools import setup

setup(
    name='token-state-relational-mapper',
    packages=['token-state-relational-mapper'],
    include_package_data=True,
    install_requires=[
        'flask',
        'web3',
        'click'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ]
)