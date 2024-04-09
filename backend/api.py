import time
import socket
import requests
import threading

import config
import endpoints
import block
import config

from flask_cors import CORS
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template

from block import Block
from transaction import Transaction
from endpoints import node, rest_api

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = config.BOOTSTRAP_IP
BOOTSTRAP_PORT = config.BOOTSTRAP_PORT



# Define the flask environment and register the blueprint with the endpoints.
app = Flask(__name__)
app.config['DEBUG']=True
app.register_blueprint(rest_api)
CORS(app)


if __name__ == '__main__':
    #Define the argument parser.
    parser = ArgumentParser(description='Rest api of BCC.')
    parser.add_argument('--nodes', type=int, help='Number of nodes', required= True)
    parser.add_argument('--port', type=int, help='Port number', required=True)
    parser.add_argument('--bootstrap', action='store_true', help='Boolean variable')


    
    # Parse the given arguments.
    args = parser.parse_args()
    port = args.port
    endpoints.n = args.nodes
    capacity = 5
    is_bootstrap = args.bootstrap

    if (is_bootstrap):
        """
        The bootstrap node (id = 0):
            - registers itself in the ring.
            - creates the genesis block.
            - creates the first transaction and adds it in the genesis block.
            - adds the genesis block in the blockchain (no validation).
            - starts listening in the desired port.
        """
    
        node.id = 0
        
        node.state[node.id] = {
        'ip': BOOTSTRAP_IP,
        'port': BOOTSTRAP_PORT,
        'public_key': node.wallet.public_key,
        'balance': 1000 * endpoints.n,
        'stake': 0
        }

        # Create the genesis block
        genesis_block = node.create_new_block()
        

        # Adds the first and only transaction in the genesis block.
        first_transaction = Transaction(sender_adress="0", receiver_adress="0", type_of_transaction="coins", amount=1000*endpoints.n, message=None, nonce=0, Signature=None)
        genesis_block.transactions.append(first_transaction)
        genesis_block.current_hash = genesis_block.calculate_hash()
        node.wallet.transactions.append(first_transaction)

        # Add the genesis block in the chain.
        node.blockchain.blocks.append(genesis_block)
        node.current_block = None

        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=BOOTSTRAP_PORT)
    else:
        """
        The rest nodes (id = 1, .., n-1):
            - communicate with the bootstrap node in order to register them.
            - starts listening in the desired port.
        """

        # Define the register address outside the function
        register_address = 'http://' + BOOTSTRAP_IP + ':' + BOOTSTRAP_PORT + '/register_node'

        # Make a request to register the node
        response = requests.post(register_address,
                                data={'public_key': node.wallet.public_key, 'ip': BOOTSTRAP_IP, 'port': port})

        if response.status_code == 200:
            print("Node initialized")
            node.id = response.json()['id']
        else:
            print("Failed to initialize node")

        # Listen in the specified address (ip:port)
        app.run(host=BOOTSTRAP_IP, port=port)