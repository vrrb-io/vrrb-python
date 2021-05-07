from os import stat
import time
import json
import binascii
from blockchain.claim import Claim
from config.blockchain_config import GENESIS_DATA, SECONDS

class Block:

    def __init__(
        self, 
        timestamp: int,  
        block_hash: str, 
        data: dict or list or None,
        claim: Claim,
        last_block_hash: str,
        ):

        self.timestamp = timestamp
        self.last_block_hash = last_block_hash
        self.block_hash = block_hash
        self.data = data
        self.claim = claim


    def __repr__(self):
        if self.claim == 'settler_claim':
            claim = self.claim
        else:
            claim = self.claim.to_json()

        return f"""Block(
            timestamp={self.timestamp}, 
            last_block_hash={self.last_block_hash},
            block_hash={self.block_hash},
            data={self.data},
            claim={claim},
            """
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def to_json(self):
        if self.claim == 'settler_claim':
            claim = self.claim
        else:
            claim = self.claim.to_json()
        return {
            'timestamp': self.timestamp, 
            'last_block_hash': self.last_block_hash, 
            'block_hash': self.block_hash,
            'data': self.data,
            'claim': claim}

    def to_bytes(self):
        block_json = self.to_json()
        block_bytes = bytes(json.dumps(block_json), 'utf-8')
        return b'0x' + binascii.hexlify(block_bytes)

    @staticmethod
    def from_bytes(block_bytes: bytearray):
        block_json = json.loads(binascii.unhexlify(
            block_bytes[2:].decode('utf-8')))
        return Block.from_json(block_json)

    @staticmethod
    def from_json(block_json):
        return Block(**block_json)
    
    @staticmethod
    def genesis():
        settler_ts = time.time_ns()
        claims = []
        for _ in range(20):
            settler_ts += (5 * SECONDS)
            claim = Claim(settler_ts, 0)
            claims.append(claim)

        return (Block(**GENESIS_DATA), claims)
    
    @staticmethod
    def is_valid_block(last_block, block):
        # ensure that the claim is valid (chain of custody, maturity, etc)
        Claim.verify(
            block.claim.get_owner_public_key(), 
            block.claim.get_claim_payload(), 
            block.claim.get_claim_signature()
            )
        if block.claim.maturation_time > time.time_ns():
            raise Exception("Claim is not mature")

        # ensure last block hash is valid
        if block.last_block_hash != last_block.block_hash:
            raise Exception("Last block hash is incorrect")

        # ensure all transactions are valid.
        # for txn in block.data['txns']:
        #     curr_txn = Txn.from_json(**txn)
        #     Txn.is_valid_txn(curr_txn)
        

