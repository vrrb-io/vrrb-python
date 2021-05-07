from config.network_config import NETWORK_PORT
import logging
import socket 
from multiprocessing import Process
from .message import GrapeVineMessage
from ..exceptions.exceptions import *
from ..util.message_codes import *
from ..util.queue_item_types import *
from .receiver import Receiver

class Sender(Process):
    """
    """

    def __init__(self, sender_id, from_ctrl_queue, to_ctrl_queue, cxn_pool):
        """
        Constructor for the sender process

        param sender_id: A unique id to derive the concrete functionality of this sender
        param from_ctrl_queue: The client send gets new commands via this queue from the responsible ctrl
        param to_ctrl_queue: This instance forwards the ctrl queue to new receiver instances
        param cxn_pool: The cxn_pool which contains all the cxns/sockets
        """

        Process.__init__(self)
        self.sender_id = sender_id
        self.from_ctrl_queue = from_ctrl_queue
        self.to_ctrl_queue = to_ctrl_queue
        self.cxn_pool = cxn_pool

    def run(self):
        """
        This is a typical run method for this sender process.
        It waits for commands from the ctrl to establish
        new cxns or to send messages to established cxnx.
        The sender gets the appropriate cxn/socket from the cxn_pool
        """

        logging.info(f"Sender {self.sender_id} started - PID: {self.pid}")

        while True:
            queue_item = self.from_ctrl_queue.get()
            queue_item_type = queue_item['type']
            print(queue_item)

            if queue_item_type == SEND_MESSAGE:
                """
                Send message to connection
                """
                message_obj = GrapeVineMessage.from_json(queue_item['message'])
                cxn_id = message_obj.get_sender_id()
                logging.info(f"{self.sender_id} | Directing message to {cxn_id}")
                try:
                    cxn = self.cxn_pool.get_cxn(cxn_id)            
                except GrapeVineIdentifierNotFound:
                    cxn = None

                if cxn:

                    if message_obj:
                        message_json = message_obj.to_json()
                        message_bytes = message_obj.to_bytes()
                        try:
                            cxn.send(message_bytes)
                            logging.debug(f'{self.sender_id} | Sent message ({message_json["code"]}) to peer -> {cxn_id}')
                        except (ConnectionResetError, ConnectionAbortedError):
                            self.cxn_pool.del_cxn(cxn_id)
                            logging.error(f"{self.sender_id} | While sending a message, the peer disconnected")
                else:
                    logging.error(f"{self.sender_id} | No cxn found in cxn pool, giving up")

            elif queue_item_type == ESTABLISH_CXN:
                """
                Establish a new connection
                """
                logging.info(f"{self.sender_id} | Establishing new connection to {queue_item['cxn_id']}")
                cxn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_host = queue_item['cxn_id']
                server_port = NETWORK_PORT['testnet']
                try:
                    cxn.connect((server_host, server_port))
                    self.cxn_pool.add_cxn(server_host, cxn, server_id=server_host)
                except ConnectionRefusedError:
                    logging.error(f"{self.sender_id} | Cannot establish connection to {queue_item['cxn_id']}")
                

                logging.info(f"{self.sender_id} | Added new cxn to the cxn pool")

                client_receiver = Receiver(
                    cxn,
                    server_host,
                    server_port,
                    self.to_ctrl_queue,
                    self.cxn_pool
                )

                client_receiver.start()
            
            elif queue_item_type == SPREAD_MESSAGE:
                message_obj = GrapeVineMessage.from_json(queue_item['message'])
                all_cxn_ids = self.cxn_pool.get_ids()
                for cxn_id in all_cxn_ids:
                    try:
                        cxn = self.cxn_pool.get_cxn(cxn_id)
                    except GrapeVineIdentifierNotFound:
                        cxn = None

                    if cxn:
                        if message_obj:
                            message_json = message_obj.to_json()
                            message_bytes = message_obj.to_bytes()
                            try:
                                cxn.send(message_bytes)
                                logging.debug(
                                    f'{self.sender_id} | Sent message ({message_json["code"]}) to peer -> {cxn_id}')
                            except (ConnectionResetError, ConnectionAbortedError):
                                self.cxn_pool.del_cxn(cxn_id)
                                logging.error(
                                    f"{self.sender_id} | While sending a message, the peer disconnected")
                else:
                    logging.error(
                        f"{self.sender_id} | No cxn found in cxn pool, giving up")




            else:
                raise GrapeVineQueueException(f"{self.sender_id} | Queue item cannot be identified. This should never happen")

if __name__ == '__main__':
    print('Running Sender outside of network main')
