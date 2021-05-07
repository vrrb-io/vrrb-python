from grapevine.util.message_codes import HANDSHAKE_RESPONSE
from grapevine.communication.message import GrapeVineMessage
import socket
import uuid
import sys
import requests

def get_ip():
    ip = '172.117.217.57'

    return ip

TESTNET_PORT = 19292
MAINNET_PORT = 9292
NETWORK_PORT = {
    'testnet': TESTNET_PORT,
    'mainnet': MAINNET_PORT
}
SEED_PEERS = [
    {'id': str(uuid.uuid4()),
     'ip': '18.218.229.217',
     'hostname': socket.gethostbyaddr('18.218.229.217')[0]
     }, ]

CONFIG_SETTINGS = {
    'GLOBAL': {
        'HOSTKEY': '/hostkey.pem'
    },
    'GRAPEVINE': {
        'cache_size': 50,
        'max_connections': 30,
        'bootstrapper': {'host':'127.0.0.1'},
        'listen_address': {'host': "0.0.0.0", 'port': f'{TESTNET_PORT}'},
        'api_address': {'host': "192.168.0.24", 'port': f'{TESTNET_PORT + 2}'},
        'max_ttl': 0
    }
}
