from config.blockchain_config import GENESIS_DATA

class Block:

    def __init__(self, timestamp: int, last_block_hash: str, block_hash: str, data: dict or list or None, **kwargs):
        self.timestamp = timestamp
        self.last_block_hash = last_block_hash
        self.block_hash = block_hash
        self.data = data
        args = [kwarg for kwarg in kwargs.keys()]
        if 'difficulty' in args:
            self.difficulty = kwargs.get('difficulty')
        else:
            self.difficulty = 'POS'
        if 'nonce' in args:
            self.nonce = kwargs.get('nonce')
        else:
            self.nonce = 'POS'

        if 'winner' in args:
            self.winner = kwargs.get('winner')
        else:
            self.winner = 'POW'

    def __repr__(self):
        return f"""Block(
            timestamp={self.timestamp}, 
            last_block_hash={self.last_block_hash},
            block_hash={self.block_hash},
            data={self.data},
            difficulty={self.difficulty},
            nonce={self.nonce},
            winner={self.winner},
            """
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(block_json):
        return Block(**block_json)
    
    @staticmethod
    def genesis():
        return Block(**GENESIS_DATA)
    