from . import app
from flask import jsonify
from token_state_relational_mapper.mapper import get_token, get_top_token_holders, get_transfers


@app.route('/api/configuration', methods=['GET'])
def get_configuration():
    return jsonify({
        'options': app.config['MapperOptions'].serialize(),
        'parity_node_uri': app.config['PARITY_NODE_URI'],
        'sql_connection': app.config['SQLALCHEMY_DATABASE_URI']
    })


@app.route('/api/token/<contract_address>')
def get_token_at_address(contract_address):
    return jsonify(get_token(contract_address))


@app.route('/api/token/<contract_address>/holders/top/<top>')
def get_top_holders_of_token(contract_address, top):
    top_holders = get_top_token_holders(contract_address, top)
    return jsonify(top_holders)


@app.route('/api/token/<contract_address>/transfers/<address>')
def token_transfers(contract_address, address):
    transfers = get_transfers(contract_address, address)
    return jsonify(transfers)
