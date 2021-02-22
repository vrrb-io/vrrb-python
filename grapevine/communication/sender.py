import logging
import socket 
from multiprocessing import Process
from .message import GrapeVineMessage
from ..exceptions.exceptions import *
from ..util.message_codes import *
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

        logging.info(f"{self.sender_id} start - PID: {self.pid}")

        while True:
            queue_item = self.from_controller_queue.get()
            message_obj = GrapeVineMessage.from_json(queue_item)
            code = message_obj.get_code()

            if code == HANDSHAKE:
                """
                Handle Handshake protocol
                """
            elif code == NEW_PEER:
                """
                Handle new peer protocol
                """
            elif code == GET_PEERS:
                """
                Handle get peers protocol
                """
            elif code == SEND_PEERS:
                """
                Handle send peers protocol
                """
            elif code == NEW_BLOCK:
                """
                Handle new block protocol
                """
            elif code == NEW_TXN:
                """
                Handle new txn protocol
                """
            elif code == NEW_CONTRACT:
                """
                Handle new contract protocol
                """
            else:
                return None
