import logging
import time
import uuid
from multiprocessing import Process
from ..exceptions.exceptions import *
from util.crypto_hash import crypto_hash

class Receiver(Process):
    """
    A client receiver is a process which receives data from a specified socket
    """
    def __init__(self, client_socket, ipv4_address, tcp_port, to_ctrl_queue, cxn_pool):
        """
        Client receiver constructor

        param client_socket: the socket from/to the affected client
        param ipv4_address: The IPv4 address of the client
        param tcp_port: The TCP port of the client
        param to_controller_queue: The queue which connects this client receiver to the responsible controller
        param cxn_pool: If the socket crashes, the cxn will be removed from the cxn pool
        """

        Process.__init__(self)
        self.client_receiver_id = crypto_hash(str(uuid.uuid4(), time.time_ns()))
        self.client_socket = client_socket
        self.cxn_id = f"{ipv4_address}:{tcp_port}"
        self.to_ctrl_queue = to_ctrl_queue
        self.cxn_pool = cxn_pool


    def run(self):
        """
        The typical run method of the client receiver process is responsible for handling
        a connection for the grapevine instance. It handles incoming messages and forwards
        them to the controller. If the cxn crashes, this method pushes a specified command
        to the responsible ctrl.
        """

        logging.info(f'Recever started: PID {self.pid}')

        try:
            self.handle_client()
        except GrapeVineClientDisconnectedException:
            logging.info(f"{self.client_receiver_id} ({self.cxn_id}) Removing cxn from the cxn pool")
            self.cxn_pool.del_cxn(self.cxn_id)
            self.to_ctrl_queue.put({
                'message': f'Connection to {self.cxn_id} lost'
            })

    def handle_client(self):
        """
        Receives new messages until the client dies. This also
        kills cxns to clients which send malformed or malicious msgs.
        Therefore it informs the responsible ctrl as well.
        """

        self.to_ctrl_queue.put({
            'message': f"New connection to {self.cxn_id}"
        })

        try:
            while True:
                message = self._receive()
                logging.debug(f"{self.client_receiver_id} ({self.cxn_id}) | Received message: {message}")
        except (GrapeVineMessageException, GrapeVineMessageFormatException) as e:
            logging.debug(f"{self.client_receiver_id} ({self.cxn_id}) | Received undecodable or invalid message: {e}")

            raise GrapeVineClientDisconnectedException(f"Lost {self.client_receiver_id} ({self.cxn_id})")

        except (ConnectionResetError, ConnectionAbortedError, GrapeVineClientDisconnectedException):
            logging.debug(f"{self.client_receiver_id} ({self.cxn_id}) | Client disconnected")

            raise GrapeVineClientDisconnectedException(f"Lost {self.client_receiver_id} ({self.cxn_id})")
    
    def _receive(self):
        """
        Receives a new message, unpacks and forwards it to the assigned ctrl.

        returns: The received message object
        """
        message = self.client_socket.recv()
        self.to_ctrl_queue.put({
            'message': f"New Message Received: {message}"
        })
        return message