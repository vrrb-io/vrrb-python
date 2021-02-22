import uuid
import time
from util.crypto_hash import crypto_hash

class GrapeVineMessage:
    def __init__(self, code, _type, headers, data, _id=crypto_hash(str(uuid.uuid4()), time.time_ns())):
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
    
    def to_json(self):
        return self.__dict__
    
    @staticmethod
    def from_json(message_json):
        return GrapeVineMessage(**message_json)
