from blockchain.homesteader import Homesteader
from txn.txn import Txn
from blockchain.miner import Miner
import logging
import os
import signal
import uuid
import time
import sys
from multiprocessing import Queue, Process
from wallet.basic_wallet import BasicWallet
from .communication.server import Server
from .communication.sender import Sender
from .communication.cxn import CxnPool
from .control.p2p_ctrl import P2PController
from .control.message_cache import GrapeVineMessageCache
from config.network_config import CONFIG_SETTINGS
from blockchain.blockchain import Blockchain
from txn.txn_pool import TxnPool
from util.crypto_hash import crypto_hash


class Node(Process):
    def __init__(self, wallet, txn_pool, config_path='E:/New_Blockchain/backend/network/grapevine/config/config.py'):
        Process.__init__(self)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='example.log',
                            filemode='w')
                    
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        self.config_path = config_path

        self.wallet = wallet
        self.txn_pool = txn_pool
    
    def signal_handler(signal, frame):
        logging.error(f'Stopping grapevine process - PID: {os.getpid()}')
        sys.exit(0)

    def start(self):
        node_id = crypto_hash(str(uuid.uuid4()), time.time_ns())
        # Register SIGINT signal
        signal.signal(signal.SIGINT, self.signal_handler)


        grapevine_config = CONFIG_SETTINGS['GRAPEVINE']
        p2p_server_address = grapevine_config['listen_address']
        bootstrapper_address = grapevine_config['bootstrapper']
        max_connections = grapevine_config['max_connections']
        cache_size = grapevine_config['cache_size']
        max_ttl = grapevine_config['max_ttl']

        p2p_cxn_pool = CxnPool(cache_size=max_connections)
        block_message_cache = GrapeVineMessageCache('BlockMessageCache', cache_size=cache_size)
        txn_message_cache = GrapeVineMessageCache('TxnMessageCache', cache_size=cache_size)
        peer_message_cache = GrapeVineMessageCache('PeerMessageCache', cache_size=cache_size)

        ctrl_to_p2p = Queue()
        p2p_to_ctrl = Queue()
        p2p_sender = Sender(node_id, p2p_to_ctrl, ctrl_to_p2p, p2p_cxn_pool)
        p2p_server = Server('testnet', p2p_to_ctrl, p2p_cxn_pool)
        self.txn_pool = txn_pool
        self.wallet = wallet

        # TODO node shouldn't need to receive a wallet, as a wallet will receive a node.
        p2p_ctrl = P2PController(
            p2p_to_ctrl, 
            ctrl_to_p2p, 
            p2p_cxn_pool, 
            p2p_server_address, 
            txn_message_cache, 
            block_message_cache, 
            peer_message_cache, 
            max_ttl, 
            bootstrapper_address
            )

        p2p_server.start()
        p2p_ctrl.start()
        p2p_sender.start()

        p2p_server.join()
        p2p_ctrl.join()
        p2p_sender.join()


        exit_codes = p2p_sender.exitcode | p2p_server.exitcode | p2p_ctrl.exitcode

        if exit_codes > 0:
            logging.error(f"GrapeVine exited with return code {exit_codes}")
        else:
            logging.info(f"GrapeVine existed with return code {exit_codes}")

if __name__ == '__main__':
    blockchain = Blockchain()
    wallet = BasicWallet(blockchain)
    txn_pool = TxnPool()
    node = Node(wallet, txn_pool)
    node.start()
    node.join()
