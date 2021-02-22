from config.blockchain_config import TRUE_MINE_RATE
import time
from util.crypto_hash import crypto_hash
from util.hex_to_binary import hex_to_binary
from blockchain.block import Block

class ProofOfWork:
    def __init__(self):
        self.version = "0.0.1"
    
    def _mine(self, last_block, data):
        payload = self.create_payload(last_block, data)
        block_hash = crypto_hash(crypto_hash(**payload))
        nonce = payload['nonce']
        difficulty = payload['difficulty']
        while not self.check_golden_hash(block_hash, difficulty):
            nonce += 1
            payload = self.create_payload(last_block, data)
            payload['nonce'] = nonce
            block_hash = crypto_hash(crypto_hash(**payload))

        return Block(payload['timestamp'], payload['last_block_hash'], block_hash, payload['data'], difficulty=payload['difficulty'], nonce=payload['nonce'])

    def create_payload(self, last_block, data) -> dict:
        timestamp = time.time_ns()
        difficulty = self.adjust_difficulty(timestamp, last_block)
        nonce = 0
        payload = {'timestamp': timestamp, 'last_block_hash': last_block.block_hash,'data': data, 'difficulty': difficulty, 'nonce': nonce}
        return payload
    
    @staticmethod
    def adjust_difficulty(new_timestamp: int, last_block: Block):
        if (new_timestamp - last_block.timestamp) < TRUE_MINE_RATE:
            return last_block.difficulty + 1
        if (last_block.difficulty -1) > 0:
            return last_block.difficulty - 1
        return 1
    
    @staticmethod
    def check_golden_hash(block_hash: str, difficulty: int) -> bool:
        difficulty_string = '0' * difficulty
        binary = hex_to_binary(block_hash)[0:difficulty]
        is_golden_hash = binary == difficulty_string
        return is_golden_hash
    
    @staticmethod
    def proof_of_work_validation(last_block, block, callback=None):
        if block.winner != 'POW':
            if block.difficulty == 'POS' and block.nonce == 'POS':
                if callback:
                    return callback(last_block, block)
        
        elif block.difficulty == 'POS' and block.nonce != 'POS':
            raise Exception("Proof of Stake block.difficulty and block.nonce must both == POS")
        elif block.difficulty != 'POS' and block.nonce == 'POS':
            raise Exception("Proof of Stake block.difficulty and block.nonce must both == POS")
        
        print(block.last_block_hash, last_block.block_hash)
        if block.last_block_hash != last_block.block_hash:
            raise Exception('block.last_block_hash does not match last_block.block_hash')
        
        if not ProofOfWork.check_golden_hash(block.block_hash, block.difficulty):
            raise Exception('Proof of Work requirement not met')
        
        if abs(last_block.difficulty - block.difficulty) > 1:
            raise Exception('Block difficulty cannot adjust by more than one')

        reconstructed_hash = crypto_hash(crypto_hash(
            block.timestamp,
            block.last_block_hash,
            block.data,
            block.nonce,
            block.difficulty
        ))

        if block.block_hash != reconstructed_hash:
            raise Exception('The block hash is incorrect')
        

if __name__ == '__main__':
    genesis_last_hash = crypto_hash(crypto_hash('genesis_last_hash'))
    genesis_hash = crypto_hash(crypto_hash('genesis_hash'))
    genesis_data = ['data_1', 'data2', 'data3']
    new_block_data = ['data4', 'data5', 'data6']
    genesis_block = Block(1, genesis_last_hash, genesis_hash, genesis_data, difficulty=1, nonce=1)
    proof_of_work = ProofOfWork(genesis_block, new_block_data)
    block = proof_of_work._mine()
    proof_of_work = ProofOfWork(block, new_block_data)
    block = proof_of_work._mine()
    proof_of_work.proof_of_work_validation(block, genesis_block)
