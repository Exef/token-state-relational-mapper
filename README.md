# Token State Relational Mapper

[![Join the chat at https://gitter.im/token-state-relational-mapper/Lobby](https://badges.gitter.im/token-state-relational-mapper/Lobby.svg)](https://gitter.im/token-state-relational-mapper/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![codebeat badge](https://codebeat.co/badges/c81778b3-120d-42d3-aec3-0b93e903e5ce)](https://codebeat.co/projects/github-com-exef-token-state-relational-mapper-master)

## Disclamer
Code below is not meant for production. It's old experiment we restored dirty so we can use its functionality in our [cryptotaxtool](https://github.com/Neufund/cryptotaxtool). You have been warned ;)

## Overview
Token state relational mapper is a service that monitors a smart contract implementing [the ERC20 token](https://theethereum.wiki/w/index.php/ERC20_Token_Standard)  interface and maps its state to relational representation.
Token contract state is not directly available via smart contract ABI and doing queries (like lists or aggregates) over many records is extremely slow. Additionally, the Solidity mapping data structure is not iterable so access to full state requires checking all transactions to token contract from its deployment.

## Setup
Clone repository:

    git clone https://github.com/Exef/token-state-relational-mapper.git
    cd token-state-relational-mapper


Specify the following keys in [config.py](https://github.com/Exef/token-state-relational-mapper/blob/master/token_state_relational_mapper/config.py) :

    SQLALCHEMY_DATABASE_URI=''  # Postgres database address
    PARITY_NODE_URI=''          # address of nodes RPC interface

Then run:

    python setup.py install
    python setup.py test



## Starting application

    export TSRM_SETTINGS=config.py
    export FLASK_APP=./token_state_relational_mapper/commands.py
    flask init_db
    flask start_mapping --start <block-number>  --end <block-number> --address <token-contract-address>

## Available commands
To check all available commands run:

    flask --help

### Start mapping
Starts the mapping proccess and creates a webserver serving web api 

    flask start_mapping --start <block-number>  --end <block-number> --address <token-contract-address> --min-block-height <number>

Parameters:

    --address [required]   
    The address of the deployed ERC20 contract to map its state.

    --start [required]
    The block number of starting block where mapper starts gathering data about the token.

    --end [optional, default='latest']
    The block number of end block where mapper ends gathering data about the token and terminates. If it is not provided, service continues watching contracts events respecting minimum block height parameter.
    
    --min-block-height [optional, default=0]
    The minimum block height of block to be mapped during watching recently mined blocks. The service never scans for blocks with a height lower than the specified value.



### Create database
Initializes database specified in config.py SQLALCHEMY_DATABASE_URI property and creates all required tables.

    flask init_db

### Drop database
Drops the database specified in config.py SQLALCHEMY_DATABASE_URI property. You have to confirm this operation in command line prompt.

    flask drop_db

## API endpoints
### Configuration
    GET /api/configuration
### Token infromation
    GET /api/token/<contract_address>
### Top token holders
    GET /api/token/<contract_address>/holders/top/<number_of_top_holders>
