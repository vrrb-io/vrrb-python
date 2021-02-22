from util.crypto_hash import crypto_hash
import uuid
import time
from wallet.basic_wallet import BasicWallet
from blockchain.blockchain import Blockchain
from util.crypto_hash import crypto_hash
from config.blockchain_config import (MINING_REWARD_INPUT, generate_reward)

class Txn:
    """
    Txn class documents an exchange from a sender to one or more recipients
    """

    def __init__(self, sender_wallet=None, recipient=None, amount=None, id=None, input=None, output=None):
        self.id = id or crypto_hash(str(uuid.uuid4()))
        self.output = output or self.create_output(sender_wallet, recipient, amount)
        self.input = input or self.create_input(sender_wallet, self.output)
    
    def create_output(self, sender_wallet, recipient, amount):

        if float(amount) > float(sender_wallet.blockchain.account_model.get_balance(sender_wallet.address)):
            raise Exception('Amount exceeds balance')

        output = {}
        output['recipient'] = [{'address': recipient, 'amount': amount}]
        output['sender'] = {
            'address': sender_wallet.address, 
            'remaining_balance': f"{(float(sender_wallet.balance) - float(amount)):.18f}"}
        sender_wallet.blockchain.account_model.update_balances(
            sender_wallet.address, -amount)
        sender_wallet.blockchain.account_model.update_balances(recipient, amount)
        return output
    
    @staticmethod
    def create_input(sender_wallet, output):
        """
        Create the transaction input
        """
        return {
            'address': sender_wallet.address,
            'amount': sender_wallet.balance,
            'public_key': sender_wallet.public_key,
            'signature': sender_wallet.sign(output),
            'timestamp': time.time_ns()
        }

    def update_txn(self, sender_wallet, recipient, amount):
        """
        Update the transaction with an existing or new recipient
        """

        if float(amount) > float(sender_wallet.balance):
            raise Exception("Amount exceeds balance")

        for i in range(len(self.output['recipient'])):
            if recipient in self.output['recipient'][i]['address']:
                self.output['recipient'][i]['amount'] = self.output['recipient'][i]['amount'] + amount
            else:
                recipient_list = self.output['recipient']
                recipient_list.append({'address': recipient, 'amount': amount})
                self.output['recipient'] = recipient_list

        if self.output['sender']['address'] == sender_wallet.address:
            self.output['sender']['remaining_balance'] = self.output['sender']['remaining_balance'] - amount
            sender_wallet.blockchain.account_model.update_balances(sender_wallet.address, -amount)
            sender_wallet.blockchain.account_model.update_balances(recipient, amount)
        
        self.input = self.create_input(sender_wallet, self.output)
    
    def to_json(self):
        """
        serialize the transaction
        """
        txn_dict = {'id': self.id, 'input': self.input, 'output': self.output}
        return txn_dict
    
    @staticmethod
    def from_json(txn_json):
        """
        deserialize a transaction json representation back into a transaction instance
        """
        return Txn(**txn_json)
    
    @staticmethod
    def is_valid_txn(txn):
        """
        Validate txns
        """

        if txn.input['address'] == MINING_REWARD_INPUT['address']:
            if len(txn.output['recipient']) > 1 > len(txn.output['recipient']):
                raise Exception("Invalid number of mining rewards")

            if float(txn['output']['recipient'][0]['amount']) > (40**4):
                raise Exception("The block reward exceeds the maximum block reward")

            return
        
        amounts = []
        for i in range(len(txn.output['recipient'])):
            amounts.append(txn.output['recipient'][i]['amount'])
        
        amounts.append(txn.output['sender']['remaining_balance'])

        output_total = sum(amounts)

        if txn.input['amount'] != output_total:
            raise Exception("Invalid txn output values, do not match amount")

        if not BasicWallet.verify(
            txn.input['public_key'],
            txn.output,
            txn.input['signature']):
            
            raise Exception('Transaction signature is invalid')
    
    @staticmethod
    def reward_txn(miner_wallet):
        """
        Generate a mining reward transaction to reward the miner
        """

        output = {}
        output['recipient'] = [{'address': miner_wallet.address, 'amount': generate_reward()}]
        miner_wallet.blockchain.account_model.update_balances(miner_wallet.address, output['recipient'][0]['amount'])
        return Txn(input=MINING_REWARD_INPUT, output=output)
    
def main():
    blockchain = Blockchain()
    wallet = BasicWallet(blockchain)
    txn = Txn(wallet, BasicWallet(blockchain).address, 15)
    txn_json = txn.to_json()
    print(f"txn_json: {txn_json}\n")
    print(f"restored_txn: {Txn.from_json(txn_json)}")
    


if __name__ == '__main__':
    main()
