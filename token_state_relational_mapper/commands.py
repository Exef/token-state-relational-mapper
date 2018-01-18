"""
Commands to run ERC20 Token State Relational Mapper. 
"""
import click, json
from os import path
from multiprocessing import Process

from token_state_relational_mapper.commands_validators import *
from . import app, db
from .mapper import Mapper, MapperOptions


@app.cli.command()
@click.option('--address', type=str, callback=validate_address_parameter,
              help='The address of the deployed ERC20 contract to map its state.')
@click.option('--start', default='contract_creation', callback=validate_start_parameter,
              help='The block number of starting block where mapper starts gathering data about the token.')
@click.option('--end', default='latest', callback=validate_end_parameter,
              help='The block number of end block where mapper ends gathering data about the token and terminates. '
                   'If it is not provided, service continues watching contracts events respecting minimum block height parameter.')
@click.option('--min-block-height', type=int, default=0, callback=validate_integer_parameter,
              help='The minimum block height of block to be mapped during watching recently mined blocks.'
                   ' The service never scans for blocks with a height lower than the specified value.')
def start_mapping(start, end, address, min_block_height):
    """Command to start application. It starts server and starts gathering state of token. """

    click.echo('Started mapping contract at address %s.' % address)
    click.echo('Starting block: %s' % start)
    click.echo('Ending block: %s' % end)

    click.echo('Connecting to parity node: %s' % app.config['PARITY_NODE_URI'])
    app.config['MapperOptions'] = MapperOptions(address, start, end, min_block_height)

    token_state_mapping_process = Process(target=map_token_state)
    token_state_mapping_process.start()

    app.run()

    if token_state_mapping_process.is_alive():
        token_state_mapping_process.terminate()


@app.cli.command()
def init_db():
    """ Initialize the database using connection string from config. """
    db.create_all()
    app.logger.warning('Initialized database under %s' % app.config['SQLALCHEMY_DATABASE_URI'])


@app.cli.command()
@click.confirmation_option(help='Are you sure you want to drop the database?')
def drop_db():
    """ Drop the database using connection string from config. """
    db.drop_all()
    app.logger.warning('Dropped database under %s' % app.config['SQLALCHEMY_DATABASE_URI'])


def map_token_state():
    options: MapperOptions = app.config['MapperOptions']
    with open(str(path.join(path.abspath(path.dirname(__file__)), 'erc20_abi.json')), 'r') as abi_definition:
        mapper = Mapper(
            ethereum_node_uri=app.config['PARITY_NODE_URI'],
            contract_address=options.contract_address,
            abi_definition=json.load(abi_definition),
            partition_size=app.config['MAX_BLOCKS_TO_MAP_AT_ONCE'],
            max_number_of_retries=app.config['MAX_NUMBER_OF_RETRIES'],
            logger=app.logger)
        mapper.start_mapping(starting_block=options.starting_block, ending_block=options.ending_block)
