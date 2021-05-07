from wallet.basic_wallet import BasicWallet
from config.blockchain_config import SECONDS
import time
from util.crypto_hash import crypto_hash

class ProofOfClaim:
    def __init__(self, claim):
        self.claim = claim
    
    def claim_is_valid(self):
        """
        check that the claim is valid
        """
        data = {self.claim.block_ts: self.claim.chain_of_custody}
        owner_verified = BasicWallet.verify(self.claim.current_owner[1], data, self.claim.current_owner[2])
        return owner_verified
    
    def claim_is_mature(self):
        claim_mature = time.time_ns() > self.claim.block_ts
        return claim_mature

    def to_json(self):
        return {'claim': self.claim.to_json()}

    def claim_hash(self):
        if self.claim_is_valid():
            valid = True
        else:
            return None
        if self.claim_is_mature():
            mature = True
        else:
            return None
        if valid and mature:
            return crypto_hash(crypto_hash(self.claim.to_json()))

if __name__ == '__main__':
    from blockchain.blockchain import Blockchain
    from multiprocessing import Queue
    from blockchain.claim import Claim
    from blockchain.claim_pool import ClaimPool
    block_timestamp = time.time_ns() + (5 * SECONDS)
    claim_queue = Queue()
    claim_pool = ClaimPool(claim_queue)
    blockchain = Blockchain(claim_pool)
    wallet = BasicWallet(blockchain=blockchain)
    for _ in range(100):
        claim = Claim(block_timestamp, 2)
        claim.acquire(wallet)
        poc = ProofOfClaim(claim)
        while True:
            poc_hash = poc.claim_hash()
            if not poc_hash:
                poc_hash = poc.claim_hash()
            else:
                break   
        print(poc.to_json())