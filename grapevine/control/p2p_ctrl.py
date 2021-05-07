from txn.txn_pool import TxnPool
from blockchain.block import Block
from grapevine.exceptions.exceptions import GrapeVineMessageFormatException
import logging
import time
from multiprocessing import Process
from util.crypto_hash import crypto_hash
from ..util.message_codes import *
from ..util.queue_item_types import *
from ..communication.message import GrapeVineMessage
from ..communication.cxn import CxnPool
from blockchain.blockchain import Blockchain
from txn.txn import Txn

class P2PController(Process):

    def __init__(
        self,
        to_p2p_queue,
        from_p2p_queue,
        p2p_cxn_pool,
        p2p_server_address,
        txn_message_cache,
        block_message_cache,
        peers_message_cache,
        max_ttl,
        bootstrapper_address=None,
        sender_id = None
    ):

        """
        P2P Controller is responsible for handling all messages
        coming into and going out of the P2P. If a P2P client sends
        a message this controller handles it.

        param to_p2p_queue: Used by the P2P layer for incoming messages and commands.
        param to_p2p_queue: Messages and commands for the P2P layer are sent through this queue
        param p2p_cxn_pool: Pool that contains all P2P cxns/clients/sockets
        param p2p_server_address: The P2P server address for this grapevine instance
        param txn_message_cache: Message cache containing all txn messages
        param block_message_cache: Message cache containing all block messages
        param peers_mesasge_cache: Message cache containing all peer sharing messages
        param max_ttl: Max. amount of hops until messages will be dropped.
        param bootstrapper_address: (optional) dict to specifiy the bootstrapper {'host': <IPv4>, 'port': <int(port)>}
        """

        Process.__init__(self)
        self.to_p2p_queue = to_p2p_queue
        self.from_p2p_queue = from_p2p_queue
        self.p2p_cxn_pool = p2p_cxn_pool
        self.p2p_server_address = p2p_server_address
        self.txn_message_cache = txn_message_cache
        self.block_message_cache = block_message_cache
        self.peers_message_cache = peers_message_cache
        self.max_ttl = max_ttl
        self.bootstrapper_address = bootstrapper_address
        self.sender_id = sender_id

    @staticmethod
    def get_blockchain_data(blockchain: Blockchain):
        return blockchain.to_json()

    @staticmethod
    def get_txn_pool_data(txn_pool: TxnPool):
        return txn_pool.to_json()

    @staticmethod
    def get_txn_data(txn: Txn):
        return txn.to_json()

    @staticmethod
    def get_block_data(block: Block):
        return block.to_json()

    def run(self):
        """
        Typical run method used to handle P2P messages and commands. It reacts on incoming messages with changing
        the state of the Grapevine internally, or by sending new messages, responses or establishing new cxns
        """

        logging.info(f"{type(self).__name__} started - PID: {self.pid}")

        # Bootstrapping
        if self.bootstrapper_address:
            logging.info(
                f"Setting bootstrapper cxn in queue | {self.bootstrapper_address}")
            bootstrapper_id = f"{self.bootstrapper_address['host']}"
            self.to_p2p_queue.put({
                'type': ESTABLISH_CXN,
                'cxn_id': bootstrapper_id
            })
        
        while True:
            # Get the queue item and check it's type
            queue_item = self.from_p2p_queue.get()
            queue_item_type = queue_item['type']
        
            # If it's a message convert from bytes to an object for processing
            if queue_item_type == RECEIVED_MESSAGE:
                # extract the actual message from the queue
                message = queue_item['message']
                # convert from bytes to an object
                message_obj = GrapeVineMessage.from_json(message)
                # get the message code to determine what kind of message it is
                # TODO: Convert message codes to headers
                message_code = message_obj.code

                if message_code == HANDSHAKE_INIT:
                    """
                    Handle handshake response
                    """
                    logging.debug(f"P2PController | Handle handshake ({HANDSHAKE_INIT}): {message}")
                    message_id = self.peers_message_cache.add_message(message)
                    
                    # TODO: Convert message headers to permanent message headers
                    if message_id:
                        try:
                            message_timestamp = message_obj.headers['time']
                            HANDSHAKE_RESPONSE_MESSAGE = GrapeVineMessage(
                                HANDSHAKE_RESPONSE, 
                                'handshake_response', 
                                {'vrrb_handshake_response': {
                                    'time': time.time_ns(),
                                    'init_client_id': crypto_hash(message_obj.sender_id),
                                    'init_message_id': crypto_hash(message_obj._id)}}, 
                                {'init_hash': {
                                    crypto_hash(message_timestamp, message_obj.sender_id, message_obj._id)}}, 
                                sender_id=self.sender_id
                            )

                            if message_id:
                                logging.info(f"P2PController | New peer initialization (id: {message_id}")
                                self.to_p2p_queue.put({
                                    'type': HANDSHAKE_RESPONSE,
                                    'message': HANDSHAKE_RESPONSE_MESSAGE.to_json()
                                })

                        except GrapeVineMessageFormatException:
                            logging.error(f"P2P Controller | Message is malformed or missing information")
                    else:
                        logging.info(f"P2PController | Discarded message (message already known)")

                elif message_code == HANDSHAKE_RESPONSE:
                    """
                    Integrate new cxn into peer cluster
                    """
                    # Send new peers known peers

                    message_sender = message_obj.sender_id

                    peers = [cxn for cxn in self.p2p_cxn_pool._cxns.keys()]
                    server_ids = []
                    for peer in peers:
                        if peer != message_sender:
                            server_ids.append((peer, self.p2p_cxn_pool._cxns[peer][CxnPool.SERVER_ID]))
                    
                    SHARE_PEERS_MESSAGE = GrapeVineMessage(
                        SEND_PEERS, 
                        'share_peers',
                        {'handshake_complete': True, 'purpose': 'share_peers', 'to': message_sender},
                        data={'peers': server_ids},
                        sender_id=self.sender_id
                        )
                    
                    #TODO get blockchain_data
                    SEND_BLOCKS_MESSAGE = GrapeVineMessage(
                        SEND_BLOCKS,
                        'send_blocks',
                        {'handshake_complete': True, 'purpose': 'send_blocks', 'to': message_sender},
                        data={'blockchain': self.get_blockchain_data()},
                        sender_id=self.sender_id
                    )

                    SEND_TXNS_MESSAGE = GrapeVineMessage(
                        SEND_TXNS,
                        'send_txns',
                        {'handshake_complete': True, 'purpose': 'send_txns', 'to': message_sender},
                        data={'txns': self.get_txn_data()},
                        sender_id=self.sender_id
                    )

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SHARE_PEERS_MESSAGE.to_json() 
                    })

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SEND_BLOCKS_MESSAGE.to_json()
                    })

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SEND_TXNS_MESSAGE.to_json()
                    })

                    logging.info(f"P2PController | Sending peers to {message_obj.sender_id}")

                elif message_code == GET_PEERS:
                    """
                    Send peer ids to requesting peer
                    """
                    message_sender = message_obj.sender_id

                    peers = [cxn for cxn in self.p2p_cxn_pool._cxns.keys()]
                    server_ids = []
                    for peer in peers:
                        if peer != message_sender:
                            server_ids.append(
                                (peer, self.p2p_cxn_pool._cxns[peer][CxnPool.SERVER_ID]))

                    SHARE_PEERS_MESSAGE = GrapeVineMessage(
                        SEND_PEERS,
                        'share_peers',
                        {'handshake_complete': True,
                            'purpose': 'share_peers', 'to': message_sender},
                        data={'peers': server_ids},
                        sender_id=self.sender_id
                    )

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SHARE_PEERS_MESSAGE.to_json()
                    })

                    logging.info(
                        f"P2PController | Sending peers to {message_obj.sender_id}")

                elif message_code == SEND_PEERS:
                    """
                    Integrate new peers and establish new connections
                    """
                    server_ids = message_obj.data['peers']
                    existing_cxns = [cxn for cxn in self.p2p_cxn_pool.keys()]
                    known_peers = []
                    for cxn in existing_cxns:
                        known_peers.append(self.p2p_cxn_pool[cxn][CxnPool.SERVER_ID])

                    for server_id in server_ids:
                        if server_id not in known_peers:
                            self.to_p2p_queue.put({
                                'type': ESTABLISH_CXN,
                                'cxn_id': server_id
                            })

                elif message_code == NEW_PEER:
                    cxn_id = message_obj.data['peer']
                    self.to_p2p_queue.put({
                        'type': ESTABLISH_CXN,
                        'cxn_id': cxn_id
                    })

                elif message_code == GET_BLOCKS:
                    """
                    Process a blocks request from peer
                    """

                    SEND_BLOCKS_MESSAGE = GrapeVineMessage(
                        SEND_BLOCKS,
                        'send_blocks',
                        {'handshake_complete': True,
                        'purpose': 'send_blocks', 'to': message_sender},
                        data={'blockchain': self.get_blockchain_data()},
                        sender_id=self.sender_id
                    )

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SEND_BLOCKS_MESSAGE.to_json()
                    })

                elif message_code == SEND_BLOCKS:
                    """
                    Validate and integrate blocks into local blockchain instance
                    """
                    blockchain_bytes = message_obj.data['blockchain']
                    new_blockchain = Blockchain.from_bytes(blockchain_bytes)
                    self.from_p2p_queue.put({'type': NEW_BLOCK_ITEM, 'data': new_blockchain.to_json()})

                elif message_code == NEW_BLOCK:
                    """
                    Validate and integrate a new block into the local blockchain instance
                    share the new block with peers
                    """
                    block_json = message_obj.data['block']
                    new_block = Block.from_json(block_json)
                    
                    if Block.is_valid_block(new_block):
                        self.to_p2p_queue.put({
                            'type': SPREAD_MESSAGE,
                            'item': new_block.to_json()
                        })

                elif message_code == GET_TXNS:
                    """
                    Process a transaction request from a peer
                    """
                    txns_json = self.get_txn_pool_data()

                    SEND_TXNS_MESSAGE = GrapeVineMessage(
                        SEND_TXNS,
                        'send_txns',
                        {'handshake_complete': True, 'purpose': 'send_txns', 'to': message_sender},
                        data={'txns': txns_json},
                        sender_id=self.sender_id
                    )

                    self.to_p2p_queue.put({
                        'type': SEND_MESSAGE,
                        'message': SEND_TXNS_MESSAGE.to_json()
                    })


                elif message_code == SEND_TXNS:
                    """
                    Validate and integrate txns into txn pool
                    """
                    txn_pool_json = message_obj.data['txns']
                    txn_pool = TxnPool.from_json(txn_pool_json)
                    for txn in txn_pool.txn_map.keys():
                        txn = Txn.from_json(txn_pool.txn_map[txn])
                        if Txn.is_valid_txn(txn):
                            self.from_p2p_queue({'type': NEW_TXN_ITEM, 'item': txn})                        

                    self.to_p2p_queue.put({
                        'type': NEW_TXN_ITEM,
                        'item': txn_pool.to_json()
                    })

                elif message_code == NEW_TXN:
                    """
                    Validate and integrate a new txn into txn pool
                    share the txn with peers
                    """
                    txn_json = message_obj.data['txn']
                    txn = Txn.from_json(txn_json)
                    self.txn_pool.set_txn(txn)
                    self.to_p2p_queue.put({
                        'type': NEW_TXN_ITEM,
                        'item': txn_json
                    })

                else:
                    pass

            elif queue_item_type == CXN_LOST:
                """
                If a connection is lost, attempt to establish a new one
                """
                item = queue_item['item']
                senders_id = item['sender_id']
                logging.debug(f"P2PController | Connection to a peer lost, trying to get a new one: {senders_id}")
                random_id = self.p2p_cxn_pool.get_random_identifier(senders_id)
                self.to_p2p_queue.put({
                    'type': ESTABLISH_CXN,
                    'cxn_id': random_id
                    })
        

            elif queue_item_type == NEW_CXN:
                """
                If a new connection is made, share it with peers
                """
                cxn_id = queue_item['cxn_id']
                NEW_PEER_MESSAGE = GrapeVineMessage(NEW_PEER, 'new_peer', {}, data={'peer': cxn_id}, sender_id=self.sender_id)
                self.to_p2p_queue.put({
                    'type': SPREAD_MESSAGE,
                    'message': NEW_PEER_MESSAGE.to_json()
                })

            elif queue_item_type == NEW_BLOCK_ITEM:
                """
                Validate new block, integrate into local blockchain, then spread new block.
                """
                #TODO: FIX THIS!!!!!!!!!!!
                item = queue_item['item']
                logging.info(f"{item}")
                NEW_BLOCK_MESSAGE = GrapeVineMessage(
                    NEW_BLOCK, 
                    'new_block', 
                    {'validated': True, 'purpose': 'new_block', 'to': 'grapevine'}, 
                    data={'block': item}, 
                    sender_id=self.sender_id
                    )

                self.block_message_cache.add_message(NEW_BLOCK_MESSAGE, valid=True)

                self.to_p2p_queue.put({
                    'type': SPREAD_MESSAGE,
                    'message': NEW_BLOCK_MESSAGE.to_json()
                })


            elif queue_item_type == NEW_TXN_ITEM:
                """
                Spread new txn
                """
                item = queue_item['item']
                NEW_TXN_MESSAGE = GrapeVineMessage(
                    NEW_TXN,
                    'new_block',
                    {'validated': True, 'purpose': 'new_txn', 'to': 'grapevine'},
                    data={'txn': item},
                    sender_id=self.sender_id
                )
                self.txn_message_cache.add_message(NEW_TXN_MESSAGE, valid=True)
                self.to_p2p_queue.put({
                    'type': SPREAD_MESSAGE,
                    'message': NEW_TXN_MESSAGE.to_json()
                })


if __name__ == '__main__':
    print("running p2pctrl outside of grapevine main")
