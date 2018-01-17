"""
Commands to run ERC20 Token State Relational Mapper. 
"""
import click, json
from os import path
from multiprocessing import Process

from token_state_relational_mapper.commands_validators import validate_address_parameter, validate_integer_parameter
from . import app, db
from .mapper import Mapper, MapperOptions


@app.cli.command()
@click.option('--address', type=str, callback=validate_address_parameter,
              help='The address of ERC20 contract to watch.')
@click.option('--start', type=int, callback=validate_integer_parameter,
              help='The starting block where mapper starts gathering data about contract.')
@click.option('--end', type=int, callback=validate_integer_parameter,
              help='The end block where mapper ends gathering data about contract and terminates.')
@click.option('--min-block-height', type=int, callback=validate_integer_parameter,
              help='The minimum block height of block to be mapped')
def start_mapping(start, end, address, min_block_height):
    """Command to start application. It starts server and starts gathering state of token. """

    click.echo('Started mapping contract at address %s.' % address)
    click.echo('Starting block: %i' % start)
    if end is not None:
        click.echo('Ending block: %i' % end)

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
    click.echo('Initialized database under %s' % app.config['SQLALCHEMY_DATABASE_URI'])


@app.cli.command()
@click.confirmation_option(help='Are you sure you want to drop the database?')
def drop_db():
    """ Drop the database using connection string from config. """
    db.drop_all()
    click.echo('Dropped database under %s' % app.config['SQLALCHEMY_DATABASE_URI'])


def map_token_state():
    options: MapperOptions = app.config['MapperOptions']
    with open(str(path.join(path.abspath(path.dirname(__file__)), 'erc20_abi.json')), 'r') as abi_definition:
        mapper = Mapper(app.config['PARITY_NODE_URI'], options.contract_address, json.load(abi_definition), app.logger)
        mapper.start_mapping(starting_block=options.starting_block, ending_block=options.ending_block)
