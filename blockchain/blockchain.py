import time
import json
import binascii
from util.crypto_hash import crypto_hash
from config.blockchain_config import SECONDS
from blockchain.block import Block
from protocol.account_model import AccountModel
from blockchain.claim_pool import ClaimPool
from blockchain.claim import Claim
from wallet.basic_wallet import BasicWallet
from txn.txn import Txn



class Blockchain:

    def __init__(self):
        genesis = Block.genesis()
        self.chain = [genesis[0]]
        self.account_model = AccountModel()
        self.claim_pool = ClaimPool()
        self.settler_claims = genesis[1]
        for claim in self.settler_claims:
            self.claim_pool.set_claim(claim)
        

    def add_block(self, claim, data, ts, miner_wallet):
        if claim.maturation_time < ts:
            claim_payload = {claim.maturation_time: claim.chain_of_custody}
            if Claim.verify(miner_wallet.public_key, claim_payload, claim.current_owner[2]):
                last_block_hash = self.chain[-1].block_hash
                data.append(Txn.reward_txn(claim.owner_wallet).to_json())
                block_payload = {
                    'timestamp': ts, 
                    'data': data,
                    'claim': claim.to_json(),
                    'last_block_hash': last_block_hash, 
                    }
                block_hash = crypto_hash(crypto_hash(block_payload))
                block = Block(ts, block_hash, data, claim, last_block_hash)
                self.chain.append(block)
                self.claim_pool.remove_claim(claim)
                self.account_model.delete_mined_claim(miner_wallet.address, claim)
                for _ in range(20):
                    next_ts = max(self.claim_pool.claim_map.keys()) + (5 * SECONDS)
                    claim = Claim(next_ts, 0)
                    self.claim_pool.set_claim(claim)
        
    def to_json(self):
        blockchain_dict = {}
        for i in range(len(self.chain)):
            blockchain_dict[i] = self.chain[i].to_json()
        return blockchain_dict
    
    def to_bytes(self):
        blockchain_json = self.to_json()
        blockchain_bytes = bytes(json.dumps(blockchain_json), 'utf-8')
        return b'0x' + binascii.hexlify(blockchain_bytes)

    def repr(self):
        """ 
            Representation of the blockchain
        """
        return f"""
        Blockchain(
            {[block.to_json() for block in self.chain]}
            )"""

    def validate_chain(self):
        for block in self.chain:
            try:
                block.is_valid_block()
            except Exception as e:
                print(f"{e}")
                return False
        return True

    def update_chain(self, new_chain):
        if len(new_chain) < len(self.chain):
            raise Exception("Incoming chain is not longer than existing chain")
        else:
            if new_chain.validate_chain():
                self.chain = new_chain
    
    @staticmethod
    def from_json(blockchain_json):
        """
        """


    @staticmethod
    def from_bytes(blockchain_bytes: bytearray):
        blockchain_json = json.loads(binascii.unhexlify(
            blockchain_bytes[2:].decode('utf-8')))
        return Blockchain.from_json(blockchain_json)

if __name__ == '__main__':
    import random
    from blockchain.claim import Claim
    from wallet.basic_wallet import BasicWallet
    from txn.txn import Txn
    settler_ts = time.time_ns()
    blockchain = Blockchain()
    wallet1 = BasicWallet(blockchain)
    wallet2 = BasicWallet(blockchain)
    wallet3 = BasicWallet(blockchain)
    for _ in range(20):
        settler_ts += (5 * SECONDS)
        claim = Claim(settler_ts, 0)
        blockchain.claim_pool.set_claim(claim)
    
    for claim in blockchain.claim_pool.claim_map:
        blockchain.claim_pool.claim_map[claim].acquire(wallet1)

    while blockchain.claim_pool.claim_map:
        claim = blockchain.claim_pool.claim_map[min(blockchain.claim_pool.claim_map.keys())]
        blockchain.add_block(claim, [], time.time_ns())
        
