import socket
import logging
import uuid
import time
import traceback
from multiprocessing import Process, Queue
from .receiver import Receiver
from .cxn import CxnPool
from util.crypto_hash import crypto_hash
from config.network_config import *

logging.basicConfig(level=logging.INFO)

class Server(Process):

    def __init__(self, network: str, message_queue: Queue, cxn_pool: CxnPool):
        Process.__init__(self)
        self._id = crypto_hash(str(uuid.uuid4()), time.time_ns()) # A unique ID for the server
        self.queue = message_queue  # A Queue object to set messages in and share among processes
        self.external_ip = get_ip() # The servers external IP
        self._host = CONFIG_SETTINGS['GRAPEVINE']['listen_address']['host'] # The listening address ip
        self.port = NETWORK_PORT[network] # The listening address port
        self.cxn_pool = cxn_pool # A connection pool object to manage all connections
    
    def run(self):

        try:
            """
            Run the server process
            """
            # Log out the server id, listening_address and process id
            logging.info(f"Server {self._id} listening at {self.external_ip}:{self.port} - PID: {self.pid}")

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initiate the server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # set socket options
            server.bind((self._host, self.port)) # bind the server to _host:port
            server.listen(5) # listen for incoming connections

            while True:
                try:
                    # Accept clients
                    _client, address = server.accept()
                    client_ip, client_port = address # unpack the address tuple
                    
                    """initiate a receiver object to receive message, provide 
                    the client socket and message queue to the receiver process"""
                    receiver = Receiver(_client,client_ip, client_port,self.queue, self.cxn_pool)
                    receiver.start()    # Start the receiver process
                    logging.info(f"New connections -> {receiver} accepted connection from {client_ip}:{client_port}") # log the new connection
                    
                    """add the connection ip, receiver object and 'server_id'
                    to the cx pool"""
                    self.cxn_pool.add_cxn(client_ip, receiver, f"{client_ip}:{self.port}") # add
                    
                    while not self.queue.empty():
                        # if the queue is not empty get the message
                        item = self.queue.get() # get the oldest item in the queue
                        logging.info(f"Message -> {item}") # log the message
                
                except Exception as e:
                    logging.debug(f"Exception in Server.run() at pid {self.pid} -> {e} --> {traceback.print_exc()}")
        except KeyboardInterrupt:
            server.close()
            print(f"Exited the process - PID {self.pid}")

if __name__ == "__main__":
    queue = Queue()
    cxn_pool = CxnPool()
    server = Server(network='testnet', message_queue=queue, cxn_pool=cxn_pool)
    try:
        server.start()
    except KeyboardInterrupt:
        server.join()