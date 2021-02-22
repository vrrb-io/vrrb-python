import time
import string
from util.crypto_hash import crypto_hash
from .lot import Lot
from blockchain.block import Block


class ProofOfStake:
    def __init__(self):
        self.stakers = {}

    def _update(self, public_key_string: str, stake: int) -> None:
        if public_key_string in self.stakers.keys():
            self.stakers[public_key_string] += stake
        else:
            self.stakers[public_key_string] = stake
        
    def get_stake(self, public_key_string: str) -> int or None:
        if public_key_string in self.stakers.keys():
            return self.stakers[public_key_string]
        else:
            return None
    
    def validator_lots(self, last_block):
        lots = []
        seed = crypto_hash(last_block)
        for validator in self.stakers.keys():
            for stake in range(self.get_stake(validator)):
                lots.append(Lot(validator, stake+1, seed))
        return lots
    
    def forger(self, seed, data) -> Block:
        lots = self.validator_lots(seed)
        block = self.winner_lot(lots, seed, data)
        return block

    @staticmethod
    def winner_lot(lots, seed, data) -> Lot:
        winner = None
        least_offset = None
        reference_hash_int = int(crypto_hash(seed, data), 16)
        for lot in lots:
            block_hash = lot.lot_hash()
            lot_int_val = int(lot.lot_hash(), 16)
            offset = abs(lot_int_val - reference_hash_int)
            if least_offset is None or offset < least_offset:
                least_offset = offset
                winner = lot
                timestamp = time.time_ns()
        
        return Block(timestamp, seed, block_hash, data, winner=winner.public_key)


if __name__ == '__main__':

    data = {'data': ['data1', 'data2', 'data3']}
    pos = ProofOfStake(data)
    pos._update('bob', 33)
    pos._update('alice', 28)
    bob_wins = 0
    alice_wins = 0
    block = Block(time.time_ns(), 'genesis_last_hash', 'genesis_hash', 'genesis_data')
    for i in range(100):
        block = pos.forger(crypto_hash(block.to_json()))
        if block.winner == 'bob':
            bob_wins += 1
        elif block.winner == 'alice':
            alice_wins += 1
    print(f"Bob wins {bob_wins} times")
    print(f"alice wins {alice_wins} times")
