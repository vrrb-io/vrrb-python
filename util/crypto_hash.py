import hashlib
import json
from .base58 import *

def crypto_hash(*args, **kwargs):
    """
    Return a sha-256 hash of the given arguments.
    """
    args = [arg for arg in args]
    for _, value in kwargs.items():
        args.append(value)
    stringified_args = sorted(map(lambda data: json.dumps(data), args))
    joined_data = ''.join(stringified_args)
    return hashlib.sha256(joined_data.encode('utf-8')).hexdigest()


def crypto_hash_ripemd160(hashed_public_key):

    h = hashlib.new('ripemd160')
    h.update(hashed_public_key.encode('utf-8'))
    return h.hexdigest()


def main():
    print(f"crypto_hash('one', 2, [3]): {crypto_hash('one', 2, [3])}")
    print(f"crypto_hash(2, 'one', [3]): {crypto_hash(2, 'one', [3])}")
    m = b58encode_check(crypto_hash_ripemd160(crypto_hash('ansOWL89!')))[0:12]
    print(m)

if __name__ == '__main__':
    main()
