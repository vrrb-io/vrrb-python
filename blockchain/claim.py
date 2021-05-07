
import time
import binascii
from txn.txn import Txn
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import json 

class Claim:
    def __init__(
        self, 
        maturation_time: int, 
        price: float, 
        chain_of_custody=None, 
        current_owner=None, 
        owner_wallet=None,
        available=True
        ):
        self.maturation_time = maturation_time
        self.price = price
        self.available = available  
        self.chain_of_custody = chain_of_custody or {}
        self.current_owner = current_owner or ()
        self.owner_wallet = owner_wallet

    def acquire(self, wallet):
        timestamp = time.time_ns()
        acquirer = wallet.address
        self.owner_wallet = wallet
        if self.chain_of_custody.keys():
            homesteader = False
        else:
            homesteader = True
        
        wallet.blockchain.account_model.balances[wallet.address] -= self.price
        wallet.blockchain.account_model.update_claims_owned(wallet.address, self)
        
        self.chain_of_custody[acquirer] = {    
            'homesteader': homesteader, 
            'acquisition_timestamp': timestamp,  
            'acquisition_price': self.price}

        data = {self.maturation_time: self.chain_of_custody}
        self.current_owner = (acquirer, wallet.public_key, wallet.sign(data))
        self.available = False
        wallet.blockchain.account_model.update_claims_owned(wallet.address, self)

    def sell(self, wallet, new_price):
        current_owner_address = self.current_owner[0]
        if current_owner_address == wallet.address:
            self.available = True
            self.price = new_price    
        else:
            raise Exception("You do not own this claim, you cannot place it for sale")

    def buy(self, buyer_wallet):
        if self.available == True:
            if buyer_wallet.balance >= self.price:
                current_owner = self.current_owner[0]
                txn = Txn(buyer_wallet, current_owner, self.price)
                self.acquire(buyer_wallet)
                self.available = False
            else:
                raise Exception("Price exceeds buyer balance")
        return txn

    def to_json(self):
        return {
            'maturation_time': self.maturation_time, 
            'price': self.price, 
            'available': self.available,
            'chain_of_custody': self.chain_of_custody,
            'current_owner': self.current_owner
            }

    def get_claim_payload(self):
        return {self.maturation_time: self.chain_of_custody}

    def get_claim_signature(self):
        return self.current_owner[-1]
    
    def get_owner_public_key(self):
        return self.current_owner[-2]
    
    def to_bytes(self):
        claim_json = self.to_json()
        claim_bytes = bytes(json.dumps(claim_json), 'utf-8')
        return b'0x' + binascii.hexlify(claim_bytes)

    @staticmethod
    def from_bytes(claim_bytes: bytearray):
        claim_json = json.loads(binascii.unhexlify(
            claim_bytes[2:].decode('utf-8')))
        return Claim.from_json(claim_json)

    @staticmethod
    def from_json(claim_json):
        return Claim(**claim_json)        

    @staticmethod
    def verify(public_key, data, signature):
        """
        verify a signature based on signer public key and data
        """
        deserialized_public_key = serialization.load_pem_public_key(
            public_key.encode('utf8'),
            default_backend()
        )

        (r, s) = signature

        try:
            deserialized_public_key.verify(encode_dss_signature(r, s), json.dumps(data).encode('utf-8'), ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False

if __name__ == '__main__':
    from wallet.basic_wallet import BasicWallet
    from blockchain.blockchain import Blockchain
    blockchain = Blockchain()
    wallet1 = BasicWallet(blockchain)
    wallet2 = BasicWallet(blockchain)
    claim = Claim(5, 0)
    claim.acquire(wallet1)
    claim.sell(wallet1, 3)
    claim.buy(wallet2)
    claim.sell(wallet2, 7)
    claim.buy(wallet1)
    claim_json = claim.to_json()
    claim_bytes = claim.to_bytes()
    recon_claim = Claim.from_json(claim_json)
    recon_bytes_claim = Claim.from_bytes(claim_bytes)

    print(f"""Claim JSON: {claim_json}
              Claim Bytes: {claim_bytes}
              Reconstructed Claim from JSON: {recon_claim}
              Reconstructed Claim from Bytes: {recon_bytes_claim}""")
    print(len(claim_bytes[2:])/2)
