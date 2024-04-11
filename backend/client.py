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

style = style_from_dict({
    Token.QuestionMark: '#1ee9d8 bold',
    Token.Selected: '#c98c1a bold',
    Token.Instruction: '',  # default
    Token.Answer: '#a9c91a bold',
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
        
class TextValidator(Validator):
    def validate(self, document):
        try:
            str(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a string',
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
    #HomeOrExit_a = prompt(HomeOrExit_q)['option']
    HomeOrExit_a = prompt(HomeOrExit_q)
    return HomeOrExit_a


def client():
    print('Initializing node...\n')
    sleep(1)
    print("Node initialized!\n")
    while True:
        print("----------------------------------------------------------------------")
        method_q = [
            {
                'type': 'list',
                'name': 'method',
                'message': 'What would you like to do?',
                'choices': ['New transaction (coins)', 'New transaction (message)', 'Stake/Unstake', 'View last transactions','View wallet transactions', 'Show balance', 'Test inputs', 'Help', 'Exit'],
                'filter': lambda val: val.lower()
            }]
        method_a = prompt(method_q, style=style)["method"]
        os.system('cls||clear')
        if method_a == 'test inputs':
            address = 'http://' + IPAddr + ':' + \
                    str(PORT) + '/api/parse_file'
            response = requests.get(address)
                
            print("[Transactions per second, Average time of block]: ", response.content.decode('utf-8'))
            if HomeOrExit() == 'exit':
                break
            else:
                os.system('cls||clear')

        elif method_a == 'new transaction (coins)':
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
            transaction_a['type_of_transaction'] = 'coins'
            transaction_a['stake'] = "nostake"
            
            print("\nConfirmation:")
            confirmation_q = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Do you want to send ' + str(transaction_a["amount"]) + ' BCCs to node ' + str(transaction_a["receiver"]) + ' (fee: '+ str(transaction_a["amount"]*0.03) + ')?',
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
                    'validate': TextValidator,
                    'filter': lambda val: str(val)
                }]
            transaction_a = prompt(transaction_q, style=style)
            transaction_a['type_of_transaction'] = 'message'
            transaction_a['stake'] = "nostake"
            
            print("\nConfirmation:")
            confirmation_q = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Do you want to send the message "' + str(transaction_a["message"]) + '" to node ' + str(transaction_a["receiver"]) + ' (fee: '+ str(len(transaction_a["message"])) + ')?',
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
                
                data= jsonpickle.decode(response.content)
                
                
                table = Texttable()
                table.set_deco(Texttable.HEADER)
                table.set_cols_dtype(['t',  # text
                                      't',  # text
                                      't',  # text
                                    #   't',  # text
                                    #   't',  # text
                                    #   't',  # text
                                      't',  # text
                                      't'])  # text
               
                table.set_cols_align(["c","c", "c", "c", "c"])
                headers = ["Sender ID", "Receiver ID","Type of transaction", "Amount", "Message"]
                rows = []
                rows.append(headers)
                rows.extend(data)
                table.add_rows(rows)
                print(table.draw() + "\n")
            except KeyError:
                pass
            except:
                print("Node is not active. Try again later.\n")
            if HomeOrExit() == 'exit':
                break
            else:
                os.system('cls||clear')
        elif method_a == 'view wallet transactions':
            print("All transactions of the wallet")
            print(
                "----------------------------------------------------------------------\n")
            address = 'http://' + IPAddr + ':' + \
                    str(PORT) + '/api/get_my_transactions'
            try:
                response = requests.get(address)
                
                data= jsonpickle.decode(response.content)
                
                
                table = Texttable()
                table.set_deco(Texttable.HEADER)
                table.set_cols_dtype(['t',  # text
                                      't',  # text
                                      't',  # text
                                    #   't',  # text
                                    #   't',  # text
                                    #   't',  # text
                                      't',  # text
                                      't'])  # text
               
                table.set_cols_align(["c","c", "c", "c", "c"])
                headers = ["Sender ID", "Receiver ID","Type of transaction", "Amount", "Message"]
                rows = []
                rows.append(headers)
                rows.extend(data)
                table.add_rows(rows)
                print(table.draw() + "\n")
            except KeyError:
                pass
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
                
            response = requests.get(address).json()
            message = response['message']
            balance = str(response['balance'])
            print(message + balance + ' BCCs staked\n')
            transaction_a = {}
            transaction_a['receiver_address'] = 0
            transaction_q = [{
                    'type': 'input',
                    'name': 'amount',
                    'message': 'Set stake amount for node to:',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                }]
            transaction_a['amount'] = prompt(transaction_q, style=style)['amount']
            transaction_a['type_of_transaction'] = 'coins'
            transaction_a['stake'] = "yesstake"
            

            print("\nConfirmation:")
            confirmation_q = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Do you want to set the stake for the node to ' + str(transaction_a["amount"]) + ' BCCs?',
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
                print("\Staking aborted.")

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
            address = 'http://' + IPAddr + ':' + str(PORT) + '/api/get_stake_balance'
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
            print("- View wallet transactions: Prints the transactions of the wallet.")
            print("- Test inputs: Use the input file and print the throuput.")
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