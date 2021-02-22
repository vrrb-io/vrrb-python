from protocol.proof_of_stake import ProofOfStake
from .block import Block
from protocol.proof_of_work import ProofOfWork
from protocol.account_model import AccountModel

class Blockchain:

    def __init__(self):
        self.chain = [Block.genesis()]
        self.account_model = AccountModel()

    
    def add_block(self, data, consensus):
        """Mine block"""
        if consensus=='pow':
            pow = ProofOfWork()
            self.chain.append(pow._mine(self.chain[-1], data))
        if consensus=='pos':
            pos = ProofOfStake()
            self.chain.append(pos.forger(seed=self.chain[-1].to_json(), data=data))

    def __repr__(self):
        """Representative printout of the Blockchain class"""

        return f'Blockchain: {self.chain}'

    def replace_chain(self, chain):
        """
        If the incoming chain is both longer and valid
        replace the local chain with the incoming chain
        """
        if len(chain) <= len(self.chain):
            raise Exception("Incoming chain must be longer to replace")

        try:
            Blockchain.is_valid_chain(chain)
        except Exception as e:
            raise Exception(f"Chain not replaced. The incoming chain is invalid: {e}")

        self.chain = chain
    

    def to_json(self):
        """Serialize blockchain"""
        return list(map(lambda block: block.to_json(), self.chain))
    
    @staticmethod
    def from_json(chain_json):
        """Deserialize blockchain"""
        blockchain = Blockchain()
        blockchain.chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))
        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """ Validate incoming chain"""

        if chain[0] != Block.genesis():
            raise Exception("The genesis block must be valid")
        
        for i in range(1, len(chain) -1):
            block = chain[i]
            last_block = chain[i-1]
            ProofOfWork.proof_of_work_validation(last_block=last_block, block=block)
        
        Blockchain.is_valid_transaction_chain(chain)
    
    @staticmethod
    def is_valid_transaction_chain(chain):
        """
        Check if the transactions in the chain are all valid
        """
        return chain


if __name__ == '__main__':
    blockchain = Blockchain()
    blockchain.add_block(['123', '345', '567', '789'], consensus='pow')
    blockchain.add_block(['123', '345', '567', '789'], consensus='pos')
    print(blockchain)
