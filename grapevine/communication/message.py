import uuid
import time
import binascii
import json

from numba.np.ufunc import parallel
from util.crypto_hash import crypto_hash

class GrapeVineMessage:
    def __init__(self, code, _type, headers, data, sender_id, _id=crypto_hash(str(uuid.uuid4()), time.time_ns())):
        """
        Message Constructor.

        param code: the message type code
        param _type: the type of message
        param headers: the message headers
        param data: the data from the message
        param _id: a unique message id
        """
        self._type = _type
        self.headers =  headers
        self.data = data
        self._id = _id
        self.sender_id = sender_id
        self.code = code
    
    def get__type(self):
        return self._type

    def get_code(self):
        return self.code
    
    def get_headers(self):
        return self.headers

    def get_data(self):
        return self.data
    
    def get__id(self):
        return self._id
    
    def get_sender_id(self):
        return self.sender_id

    def to_json(self):
        return self.__dict__

    def to_bytes(self):
        msg = self.to_json()
        msg_bytes = bytes(json.dumps(msg), 'utf-8')
        return b'0x' + binascii.hexlify(msg_bytes)

    @staticmethod
    def from_bytes(message_bytes: bytearray):
        msg_json = json.loads(binascii.unhexlify(message_bytes))
        return GrapeVineMessage.from_json(msg_json)

    @staticmethod
    def from_json(message_json):
        return GrapeVineMessage(**message_json)

if __name__ == '__main__':
    import time
    from blockchain.claim import Claim
    from blockchain.block import Block
    from blockchain.blockchain import Blockchain
    from wallet.basic_wallet import BasicWallet
    from txn.txn import Txn
    print('Running message without a network')
    start_time = time.time()
    for _ in range(250):
        txn = Txn(BasicWallet(Blockchain()), BasicWallet(Blockchain()).address, 33)
        message = GrapeVineMessage(1, 'test_txn', 0x0123456789ab, txn.to_json(), str(uuid.uuid4()))
        bytes_msg = message.to_bytes()
        msg = GrapeVineMessage.from_bytes(bytes_msg)
        data = msg.data
        txn = Txn.from_json(data)
        is_valid = Txn.is_valid_txn(txn)
    end_time = time.time()
    print(end_time - start_time)
    