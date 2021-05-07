import json

from numpy import sign
from util.crypto_hash import crypto_hash, crypto_hash_ripemd160
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from config.blockchain_config import STARTING_BALANCE, VRRB_TESTNET, VRRB_MAINNET
from util.base58 import b58encode, b58decode, b58encode_check, b58decode_check
from protocol.account_model import AccountModel

class BasicWallet:

    def __init__(self, blockchain, address=None, network=VRRB_TESTNET, private_key=None):
        self.blockchain = blockchain
        self.private_key = private_key if private_key else ec.generate_private_key(ec.SECP256K1(), default_backend())
        self.public_key = self.private_key.public_key()
        self.serialize_public_key()
        self.address = address if address else (network['wallet_byte_prefix'] + b58encode_check(crypto_hash_ripemd160(crypto_hash(self.public_key)))).decode('utf-8')
        self.pk_hash = crypto_hash(str(self.private_key))
        if network == VRRB_TESTNET:
            self.blockchain.account_model.add_account(self.address, self.pk_hash)
            self.blockchain.account_model.update_balances(self.address, self.pk_hash, STARTING_BALANCE)

    def restore_wallet(self, private_key, blockchain):
        if self.blockchain:
            for account in self.blockchain.account_model.accounts:
                address, pk_hash = account
                if crypto_hash(str(private_key)) == pk_hash:
                    self = BasicWallet(address, blockchain, private_key)

    @property
    def balance(self):
        """
        Return the balance of the address
        """
        return self.blockchain.account_model.get_balance(self.address)
    
    @property
    def claims_owned(self):
        """
        return a list of claims owned by the address
        """
        return self.blockchain.account_model.get_claims_owned(self.address, self.pk_hash)

    def sign(self, data):
        """
        Generate signature based on data using the local private key
        """
        return decode_dss_signature(self.private_key.sign(
            json.dumps(data).encode('utf-8'), ec.ECDSA(hashes.SHA256())
        ))
    
    def serialize_public_key(self):
        """
        Reset the public key to it's serialized version
        """

        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
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



def main():
    wallet = BasicWallet()
    data = {'foo': 'bar'}
    signature = wallet.sign(data)
    print(f"address: {wallet.address}")
    print(f"signature: {signature}")
    valid_signature = BasicWallet.verify(wallet.public_key, data, signature)
    print(f'valid_signature: {valid_signature}')
    invalid_signature = BasicWallet.verify(BasicWallet().public_key, data, signature)
    print(f"invalid_signature: {invalid_signature}")

if __name__ == '__main__':
    main()
