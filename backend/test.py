import requests
import socket
import pickle
import os
import config
import jsonpickle

from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from argparse import ArgumentParser
from texttable import Texttable
from time import sleep

# Get the IP address of the device
if config.LOCAL:
    IPAddr = '127.0.0.1'
else:
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
PORT = 5000

def test_coins():
    print("---starting")
    for i in range(0,5):
        address = 'http://' + IPAddr + ':' + \
                            str(PORT) + '/api/create_transaction'
        transaction = {}
        transaction["amount"] = 1
        transaction["receiver"] = 1
        transaction['type_of_transaction'] = 'coins'
        transaction['stake'] = "nostake"
        response = requests.post(
            address, data=transaction).json()
        message = response["message"]
    print("\n" + message + '\n')
    
def test_messages():
    print("---starting")
    for i in range(0,5):
        address = 'http://' + IPAddr + ':' + \
                            str(PORT) + '/api/create_transaction'
        transaction = {}
        transaction["message"] = "hello"
        transaction["receiver"] = 1
        transaction['type_of_transaction'] = 'message'
        transaction['stake'] = "nostake"
        response = requests.post(
            address, data=transaction).json()
        message = response["message"]
    print("\n" + message + '\n')

if __name__ == "__main__":

    #test_coins()
    test_messages()


