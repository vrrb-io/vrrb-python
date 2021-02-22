from util.crypto_hash import crypto_hash

class Lot:
    def __init__(self, public_key, iteration, last_block_hash):
        self.public_key = public_key
        self.iteration = iteration
        self.last_block_hash = last_block_hash
    
    def lot_hash(self):
        hash_data = self.public_key + self.last_block_hash
        for i in range(self.iteration):
            hash_data = crypto_hash(crypto_hash(hash_data, i))
        return hash_data
    
    def __repr__(self):
        return(
            f"""Lot(
                public_key={self.public_key},
                iteration={self.iteration}
                last_block_hash={self.last_block_hash}
                

            )"""
        )