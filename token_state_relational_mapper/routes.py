from . import app
from flask import jsonify


@app.route('/api/configuration', methods=['GET'])
def get_configuration():
    return jsonify({
        'options': app.config['MapperOptions'].serialize(),
        'parity_node_uri': app.config['PARITY_NODE_URI'],
        'sql_connection': app.config['DATABASE_URI']
    })