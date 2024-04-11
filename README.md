# DistributedSystems
Test for 2 nodes by running:

python api.py --nodes 2 --port 5000 --bootstrap
python api.py --nodes 2 --port 5001

on different terminals and then make transactions using the client by running:

python client.py -p 5000 
or
python client.py -p 5001
