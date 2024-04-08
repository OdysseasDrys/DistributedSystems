import requests
import socket
import pickle
import os
import config

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

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))


def HomeOrExit():
    HomeOrExit_q = [
        {
            'type': 'list',
            'name': 'option',
            'message': 'What do you want to do?',
            'choices': ['Home', 'Exit'],
            'filter': lambda val: val.lower()
        }]
    HomeOrExit_a = prompt(HomeOrExit_q)['option']
    return HomeOrExit_a


def client():
    print('Initializing node...\n')
    sleep(2)
    print("Node initialized!\n")
    while True:
        print("----------------------------------------------------------------------")
        method_q = [
            {
                'type': 'list',
                'name': 'method',
                'message': 'What would you like to do?',
                'choices': ['New transaction (coins)', 'New transaction (message)', 'Stake/Unstake', 'View last transactions', 'Show balance', 'Help', 'Exit'],
                'filter': lambda val: val.lower()
            }]
        method_a = prompt(method_q, style=style)["method"]
        os.system('cls||clear')
        if method_a == 'new transaction (coins)':
            print("New transaction (coins)!")
            print(
                "----------------------------------------------------------------------")
            transaction_q = [
                {
                    'type': 'input',
                    'name': 'receiver',
                    'message': 'Receiver (type receiver\'s id):',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                },
                {
                    'type': 'input',
                    'name': 'amount',
                    'message': 'Amount:',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                }]
            transaction_a = prompt(transaction_q, style=style)
            print("\nConfirmation:")
            confirmation_q = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Do you want to send ' + str(transaction_a["amount"]) + ' BCCs to node ' + str(transaction_a["receiver"]) + '?',
                    'default': False
                }
            ]
            confirmation_a = prompt(confirmation_q)["confirm"]
            if confirmation_a:
                address = 'http://' + IPAddr + ':' + \
                    str(PORT) + '/api/create_transaction'
                try:
                    response = requests.post(
                        address, data=transaction_a).json()
                    message = response["message"]
                    print("\n" + message + '\n')
                    try:
                        balance = response["balance"]
                        print("----------------------------------")
                        print("Your current balance is: " +
                              str(balance) + " BCCs")
                        print("----------------------------------\n")
                    except KeyError:
                        pass
                except:
                    print("\nNode is not active. Try again later.\n")
                if HomeOrExit() == 'exit':
                    break
                else:
                    os.system('cls||clear')
            else:
                print("\nTransaction aborted.")

        elif method_a == 'new transaction (message)':
            print("New transaction (message)!")
            print(
                "----------------------------------------------------------------------")
            transaction_q = [
                {
                    'type': 'input',
                    'name': 'receiver',
                    'message': 'Receiver (type receiver\'s id):',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                },
                {
                    'type': 'input',
                    'name': 'message',
                    'message': 'Message:',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                }]
            transaction_a = prompt(transaction_q, style=style)
            print("\nConfirmation:")
            confirmation_q = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Do you want to send the message "' + str(transaction_a["message"]) + '" to node ' + str(transaction_a["receiver"]) + '?',
                    'default': False
                }
            ]
            confirmation_a = prompt(confirmation_q)["confirm"]
            if confirmation_a:
                address = 'http://' + IPAddr + ':' + \
                    str(PORT) + '/api/create_transaction'
                try:
                    response = requests.post(
                        address, data=transaction_a).json()
                    message = response["message"]
                    print("\n" + message + '\n')
                    try:
                        balance = response["balance"]
                        print("----------------------------------")
                        print("Your current balance is: " +
                              str(balance) + " BCCs")
                        print("----------------------------------\n")
                    except KeyError:
                        pass
                except:
                    print("\nNode is not active. Try again later.\n")
                if HomeOrExit() == 'exit':
                    break
                else:
                    os.system('cls||clear')
            else:
                print("\nTransaction aborted.")

        elif method_a == 'view last transactions':
            print("Last transactions (last valid block in the blockchain)")
            print(
                "----------------------------------------------------------------------\n")
            address = 'http://' + IPAddr + ':' + \
                str(PORT) + '/api/get_transactions'
            try:
                response = requests.get(address)
                data = pickle.loads(response._content)
                table = Texttable()
                table.set_deco(Texttable.HEADER)
                table.set_cols_dtype(['t',  # text
                                      't',  # text
                                      't',  # text
                                      't',  # text
                                      't'])  # text
                table.set_cols_align(["c", "c", "c", "c", "c","c"])
                headers = ["Sender ID", "Receiver ID","Type of transaction", "Amount or message", "BCC used"]
                rows = []
                rows.append(headers)
                rows.extend(data)
                table.add_rows(rows)
                print(table.draw() + "\n")
            except:
                print("Node is not active. Try again later.\n")
            if HomeOrExit() == 'exit':
                break
            else:
                os.system('cls||clear')
        elif method_a == 'stake/unstake':
            print("Stake amount for the node")
            print(
                "----------------------------------------------------------------------\n")
            address = 'http://' + IPAddr + ':' + \
                str(PORT) + '/api/get_stake_balance'
            try:
                response = requests.get(address).json()
                message = response['message']
                balance = str(response['balance'])
                print(message + balance + ' BCCs staked\n') #todo: stake/unstake, if amount>stake transaction to node 0, else transaction from node 0
            except:
                print("Node is not active. Try again later.\n")
            if HomeOrExit() == 'exit':
                break
            else:
                os.system('cls||clear')

        elif method_a == 'show balance':
            print("Your balance")
            print(
                "----------------------------------------------------------------------\n")
            address = 'http://' + IPAddr + ':' + str(PORT) + '/api/get_balance'
            try:
                response = requests.get(address).json()
                message = response['message']
                balance = str(response['balance'])
                print(message + balance + ' BCCs\n')
            except:
                print("Node is not active. Try again later.\n")
            if HomeOrExit() == 'exit':
                break
            else:
                os.system('cls||clear')
        elif method_a == 'help':
            print("Help")
            print(
                "----------------------------------------------------------------------")
            print("You have the following options:")
            print("- New transaction: Creates a new transaction. You are asked for the type of transaction and then for the id of the receiver node and the amount of BCCs or message you want to send.")
            print("- Stake/Unstake: View the current staked amount of this node and choose the new stake amount you want to set.")
            print("- View last transactions: Prints the transactions of the last validated block of the Blockchat blockchain.")
            print("- Show balance: Prints the current balance of your wallet.")
            print("- Help: Prints usage information about the options.\n")

            if HomeOrExit() == 'Exit':
                break
            else:
                os.system('cls||clear')

        else:
            break


if __name__ == "__main__":
    # Define the argument parser.
    parser = ArgumentParser(description='CLI client of Blockchat.')
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-p', type=int, help='port to listen on', required=True)

    # Parse the given arguments.
    args = parser.parse_args()
    PORT = args.p

    # Call the client function.
    client()