import pickle
import node
import jsonpickle
import requests


    
from flask import Blueprint, jsonify, request

from node import Node

#Initialize the node
node = Node()
n = 0
node.state = []
rest_api = Blueprint('rest_api', __name__)

@rest_api.route('/get_block', methods=['POST'])
def get_block():
    '''Endpoint that gets an incoming block, validates it and adds it in the
        blockchain.

        Input:
            new_block: the incoming block in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    new_block = pickle.loads(request.get_data())
    
    
    if node.validate_block(new_block):
        node.blockchain.blocks.append(new_block)
        node.create_new_block()
        print("------ Successfully added block")
        return jsonify({'message': "OK"}), 200
    else:
       return jsonify({'mesage': "Block rejected."}), 409

@rest_api.route('/register_node', methods=['POST'])
def register_node():
    '''Endpoint that registers a new node in the network.
        It is called only in the bootstrap node.

        Input:
            public_key: the public key of node to enter.
            ip: the ip of the node to enter.
            port: the port of the node to enter.

        Returns:
            id: the id that the new node is assigned.
    '''
    # Get the arguments
    node_key = request.form.get('public_key')
    node_ip = request.form.get('ip')
    
    node_port = request.form.get('port')
    node_id = len(node.state)
    #node_boot_ip = request.form.get('ip')
    #node_ip = node_boot_ip[:-1] + str(node_id)
    
    # Add node in the list of registered nodes.
    node.state.append({
        'id': node_id, 
        'ip': node_ip, 
        'port': node_port, 
        'public_key': node_key, 
        'balance': 0,
        'stake': 0
    })
    
    # When all nodes are registered, the bootstrap node sends them:
    # - the current chain
    # - the state
    # - the first transaction
    
    if (node_id == n - 1 ): 
        for state_node in node.state:
            if state_node['id'] != node.id:
                node.share_blockchain(state_node)
                node.share_state(state_node)
        # print("---after sharing blockchain and state: ",state_node)
        for state_node in node.state:
            # print("------state_node2: ", state_node)
            #print("---auto: ",state_node)
            if state_node['id'] != node.id:
                node.create_transaction(state_node['public_key'], 'first', 1000, "-")
                print("Sent 1000 BCC to node ", state_node["id"])
                
                # address = 'http://' + state_node['ip'] + ':' + state_node['port']
                # response = requests.post(address + '/get_block',
                #                          data=pickle.dumps(node.current_block))
                # if response.status_code != 200:
                #     print("Failed to send block")
                #     break          
                


    return jsonify({'id': node_id}), 200

@rest_api.route('/', methods=['GET', 'POST'])
def hello():
    print("Hello")
    return jsonify({'message': "OK"}), 200

@rest_api.route('/validate_transaction', methods=['POST'])
def validate_transaction():
    '''Endpoint that gets an incoming transaction and valdiates it.

        Input:
            new_transaction: the incoming transaction in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    # print("EFTASE EDW - 56")
    new_transaction = pickle.loads(request.get_data())
    # print("EFTASE EDW - 57")
    # print(new_transaction)
    # print(jsonpickle.encode(new_transaction))
    if node.validate_transaction(new_transaction):
        return jsonify({'message': "OK"}), 200
    else:
        # print("eimai sto endpoint")
        return jsonify({'message': "The signature is not authentic"}), 401


@rest_api.route('/get_transaction', methods=['POST'])
def get_transaction():
    '''Endpoint that gets an incoming transaction and adds it in the
        block.

        Input:
            new_transaction: the incoming transaction in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''

    new_transaction = pickle.loads(request.get_data())
    # if node.add_transaction_to_block(new_transaction):
    #     return jsonify({'message': "OK"}), 200
    # else:
    #     return jsonify({'message': "The block was not added"}), 401
    if (node.wallet.public_key == new_transaction.receiver_address):
        if (new_transaction.type_of_transaction =='coins' or new_transaction.type_of_transaction =='first'):
            node.balance += new_transaction.amount


    #node.add_transaction_to_block(new_transaction)
    if not node.add_transaction_to_block(new_transaction): 
            
            print("-------new_block--------")
            validator = node.proof_of_stake(node.current_block.previous_hash)
            
            node.broadcast_block(validator) 
            print("Broadcasted Block")  
    return jsonify({'message': "OK"}), 200
    # else:
    #     return jsonify({'message': "The block was not added"}), 401

@rest_api.route('/get_state', methods=['POST'])
def get_state():
    '''Endpoint that gets a state (information about other nodes).

        Input:
            state: the state in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''
    node.state = pickle.loads(request.get_data())
    # Update the id of the node based on the given state.
    for state_node in node.state:
        if state_node['public_key'] == node.wallet.public_key:
            node.id = state_node['id']
    return jsonify({'message': "OK"})


@rest_api.route('/get_blockchain', methods=['POST'])
def get_blockchain():
    '''Endpoint that gets a blockchain.

        Input:
            blockchain: the blockchain in pickle format.
        Returns:
            message: the outcome of the procedure.
    '''

    node.blockchain = pickle.loads(request.get_data())
    #if node.validate_chain():
    # node.blockchain = jsonpickle.decode(request.get_data())
    # return jsonpickle.encode(request.get_data())
    return jsonify({'message': "OK"})
    #else:
    #   return jsonify({"message": "Chain validation failed."}), 400

@rest_api.route('/send_chain', methods=['GET'])
def send_chain():
    '''Endpoint that sends a blockchain.

        Returns:
            the blockchain of the node in pickle format.
    '''
    return jsonpickle.encode(node.blockchain)
    #return pickle.dumps(node.blockchain)

@rest_api.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    '''Endpoint that creates a new transaction.

        Input:
            receiver: the id of the receiver node.
            type_of_transaction: the type of the transaction.
            amount: the amount of BCCs to send.
            message: the message of the transaction.
        Returns:
            message: the outcome of the procedure.
    '''

    # Get the arguments.
    stake = request.form.get('stake')
    #print("--- is it stake:", stake)
    type_of_transaction = request.form.get('type_of_transaction')
    amount = request.form.get('amount')
    if amount != None:
            amount = int(amount)
    message = request.form.get('message')
    #print("--- amount is ", amount)
    if stake == 'nostake':
        receiver_id = int(request.form.get('receiver'))
        # Find the address of the receiver.
        receiver_public_key = None
        for state_node in node.state:
            if (state_node['id'] == receiver_id):
                receiver_public_key = state_node['public_key']
    
        if (receiver_public_key and receiver_id != node.id):
            if node.create_transaction(receiver_public_key, type_of_transaction, amount, message):
                return jsonify({'message': 'The transaction was successful.', 'balance': node.wallet.get_balance(node)}), 200
            else:
                return jsonify({'message': 'Not enough BCCs.', 'balance': node.wallet.get_balance(node)}), 400
        else:
            return jsonify({'message': 'Transaction failed. Wrong receiver id.'}), 400
    elif stake == 'yesstake':
        receiver_public_key = 0
        if amount != node.wallet.get_stake_balance(node):
            try: 
                if node.create_transaction(receiver_public_key, type_of_transaction, amount, message):
                    return jsonify({'message': 'The transaction was successful.', 'balance': node.wallet.get_balance(node)}), 200
                else:
                    return jsonify({'message': 'Not enough BCCs.', 'balance': node.wallet.get_balance(node)}), 400
            except:
                return jsonify({'message': 'Transaction failed. Wrong receiver id.'}), 400
        elif amount == node.wallet.get_balance(node):
            return jsonify({'message': 'Amount is already staked. No transactions completed.'}), 200
        # elif amount < node.wallet.get_balance(node):
        #     try: 
        #         if node.create_transaction(node.wallet.public_key, type_of_transaction, amount, message):
        #             return jsonify({'message': 'The transaction was successful.', 'balance': node.wallet.get_balance(node)}), 200
        #         else:
        #             return jsonify({'message': 'Not enough BCCs.', 'balance': node.wallet.get_balance(node)}), 400
        #     except:
        #         return jsonify({'message': 'Transaction failed. Wrong receiver id.'}), 400


@rest_api.route('/api/get_balance', methods=['GET'])
def get_balance():
    '''Endpoint that returns the current balance of the node.

        Returns:
            message: the current balance.
    '''
    return jsonify({'message': 'Current balance: ', 'balance': node.wallet.get_balance(node)})


@rest_api.route('/api/get_stake_balance', methods=['GET'])
def get_stake_balance():
    '''Endpoint that returns the current stake balance of the node.

        Returns:
            message: the current stake balance.
    '''
    return jsonify({'message': 'Current stake balance: ', 'balance': node.wallet.get_stake_balance(node)})

@rest_api.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    '''Endpoint that returns the transactions of the last confirmed block.

        Returns:
            a formatted list of transactions in pickle format.
    '''
    #if len(node.blockchain.blocks[-1].transactions)==0:
     #   return jsonify({'message': 'There are no transactions in the last block.'}), 400
    #else:
        # return jsonpickle.encode(node.blockchain.blocks[-1].transactions)
    print(node.blockchain.blocks)
    return jsonpickle.encode([transaction.to_list() for transaction in node.blockchain.blocks[-1].transactions])
        #return jsonify(len(node.blockchain.blocks[-1].transactions)) # comment the above to see the number of transactions in the last block


@rest_api.route('/api/get_my_transactions', methods=['GET'])
def get_my_transactions():
    '''Endpoint that returns all the transactions of a node (as a sender of receiver).

        Returns:
            a formatted list of transactions in pickle format.
    '''
    if len(node.wallet.transactions)==0:
        return jsonify({'message': 'There are no transactions in the wallet.'}), 400
    else:
        return jsonpickle.encode([transaction.to_list() for transaction in node.wallet.transactions])
        return pickle.dumps([transaction.to_list() for transaction in node.wallet.transactions])
        return jsonify(len(node.wallet.transactions)) # comment the above to see the number of transactions in the wallet


@rest_api.route('/api/get_id', methods=['GET'])
def get_id():
    '''Endpoint that returns the id of the node.

        Returns:
            message: the id of the node.
    '''
    return jsonify({'message': node.id})

@rest_api.route('/api/parse_file', methods=['GET'])
def parse_file():
    # node.parse_file()
    '''Endpoint that returns the id of the node.

        Returns:
            message: the id of the node.
    '''
    transactions_per_sec, avg_block_duration = node.parse_file()
    #print(str(transactions_per_sec), str(avg_block_duration))
    
    return jsonify({'transactions_per_sec': str(transactions_per_sec) , 'avg_block_duration': str(avg_block_duration)})

