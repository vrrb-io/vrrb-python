import socket
import uuid
import sys
import requests

def get_ip():

    page = requests.get("https://jsonip.com")
    ip = page.json()['ip']

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

CONN_MESSAGE = {'header': 'welcome', 'id': 1, 'content': 'thank you for connecting',
                'ip': get_ip(), 'uri': f'ws://{get_ip()}:{TESTNET_PORT}'}

CONFIG_SETTINGS = {
    'GLOBAL': {
        'HOSTKEY': '/hostkey.pem'
    },
    'GRAPEVINE': {
        'cache_size': 50,
        'max_connections': 30,
        'bootstrapper': '',
        'listen_address': {'host': "0.0.0.0", 'port': f'{TESTNET_PORT}'},
        'api_address': {'host': "192.168.0.24", 'port': f'{TESTNET_PORT + 2}'},
        'max_ttl': 0
    }
}
