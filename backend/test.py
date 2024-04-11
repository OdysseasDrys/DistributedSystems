import requests
import socket
import pickle
import os
import config
import jsonpickle
import random
import string

from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from argparse import ArgumentParser
from texttable import Texttable
from time import sleep
import threading
# Get the IP address of the device
if config.LOCAL:
    IPAddr = '127.0.0.1'
else:
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
PORT = 5000

def generate_random_message(length=5):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def test_coins():
    print("---starting")
    for i in range(0,5):
        address = 'http://' + IPAddr + ':' + \
                            str(PORT) + '/create_transaction'
        transaction = {}
        transaction["amount"] = 1
        transaction["receiver"] = 1
        transaction['type_of_transaction'] = 'coins'
        transaction['stake'] = "nostake"
        response = requests.post(
            address, data=transaction).json()
        message = response["message"]
    print("\n" , message , '\n')
    
def test_messages():
    print("---starting")
    for i in range(0,5):
        address = 'http://' + IPAddr + ':' + \
                            str(PORT) + '/create_transaction'
        transaction = {}
        transaction["message"] = generate_random_message()
        transaction["receiver"] = 1
        transaction['type_of_transaction'] = 'message'
        transaction['stake'] = "nostake"
        response = requests.post(
            address, data=transaction).json()
        message = response["message"]
    print("\n" + message + '\n')

def run_test():
    address = 'http://' + IPAddr + ':' + \
                    str(PORT) + '/parse_file'
    response = requests.get(address).json()
    return response

def run_test_on_server(IPAddr, PORT):
    address = f'http://{IPAddr}:{PORT}/parse_file'
    response = requests.get(address).json()
    t = str(response["transactions_per_sec"])
    b = str(response["avg_block_duration"])
    print(f"\ntransactions_per_sec: {t}\navg_block_duration: {b}\n")


if __name__ == "__main__":

    servers = [
        {'IPAddr': IPAddr, 'PORT': 5000},
        {'IPAddr': IPAddr, 'PORT': 5001},
        {'IPAddr': IPAddr, 'PORT': 5002},
        {'IPAddr': IPAddr, 'PORT': 5003},
        {'IPAddr': IPAddr, 'PORT': 5004},
    ]

    threads = []
    for server in servers:
        thread = threading.Thread(target=run_test_on_server, args=(server['IPAddr'], server['PORT']))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


    
