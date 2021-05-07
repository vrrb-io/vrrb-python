from config.blockchain_config import SECONDS
from grapevine.communication.message import GrapeVineMessage
from grapevine.util.message_codes import *
import time
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from blockchain.blockchain import Blockchain
from txn.txn import Txn
from txn.txn_pool import TxnPool
from wallet.basic_wallet import BasicWallet

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
blockchain = Blockchain()
wallet = BasicWallet(blockchain)
txn_pool = TxnPool()

@app.route('/')
def route_default():
    return "Welcome to the VRRB Blockchain"

@app.route('/blockchain')
def route_blockchain():
    return jsonify(blockchain.to_json())

@app.route('/blockchain/range')
def route_blockchain_range():
    start = int(request.args.get("start"))
    end = int(request.args.get("end"))

    return jsonify(blockchain.to_json()[::-1][start:end])

@app.route('/blockchain/length')
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

@app.route('/blockchain/appropriate')
def route_appropriate_claim():
    txn_data = txn_pool.txn_data()
    first_claim = min(wallet.claims_owned.keys())
    blockchain.add_block(
        blockchain.claim_pool.claim_map[first_claim],
        txn_data, 
        time.time_ns(),
        wallet
        )
    block = blockchain.chain[-1]
    message = GrapeVineMessage(NEW_BLOCK, "new_block", "new_block_appropriated", block.to_json(), sender_id=wallet.address)
    print(message.data)
    txn_pool.clear_txns(blockchain)
    return jsonify(block.to_json())

@app.route('/wallet/transact', methods=['GET', 'PUT', 'POST'])
def route_wallet_transact():
    txn_amount = float(request.args.get('amount'))
    txn_recipient = request.args.get('to')
    txn = txn_pool.existing_txn(wallet.address)

    if txn:
        txn.update_txn(
            wallet,
            txn_recipient,
            txn_amount
        )

    else:

        txn = Txn(
            wallet,
            txn_recipient,
            txn_amount
        )

        txn_pool.set_txn(txn)

    message = GrapeVineMessage(NEW_TXN, 'new_txn', 'new_transaction', txn.to_json(), sender_id=wallet.address)
    return redirect('/wallet/info')

@app.route('/wallet/info')
def route_wallet_info():
    return jsonify({ 'address': wallet.address, 'balance': wallet.balance})

@app.route('/known-addresses')
def route_known_addresses():
    known_addresses = set()

    for block in blockchain.chain:
        for txn in block.data:
            addresses = []
            for i in range(len(txn['output']['recipient'])):
                addresses.append(txn['output']['recipient'][i]['address'])
            known_addresses.update(addresses)
    
    return jsonify(list(known_addresses))

@app.route('/txns')
def route_txns():
    return jsonify(txn_pool.txn_data())

@app.route('/homestead_claims')
def route_homestead_claims():
    for claim in blockchain.claim_pool.claim_map.values():
        if claim.available:
            if claim.price == 0:
                claim.acquire(wallet)
                blockchain.claim_pool.update_claim(claim)
    
    return jsonify(wallet.claims_owned)

@app.route('/claims')
def route_claims():
    return jsonify(blockchain.claim_pool.to_json())

if __name__ == '__main__':
    app.run(port=5002)
