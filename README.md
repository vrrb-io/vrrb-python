# VRRB: The Variable Random Reward Blockchain

### VRRB utilizes a Proof of Claim consensus algorithm, a homesteading approach to block creation

This project is coming soon, and is not ready for deployment. If you would like to contribute, first
clone the repository to local

```
git clone https://github.com/vrrb-io/vrrb-python.git
```

Install requirements:

```
pip install -r requirements.txt
```

To run the simple Flask App/API

```
python -m backend.app
```

Visit the link to the localhost:port where the app is being served

The following instructions are for different routes

To see available claims:
    /claims

To homestead claims:
    /homstead_claims

To mine claims:
    /blockchain/appropriate

If the claim is not yet mature (current time is less than 
claim maturation time) a new block will not be mined

To see wallet information:
    /wallet/info

To see entire blockchain:
    /blockchain

To execute a (fake) transaction for 10  coins to a fake recipient (try this before mining a claim):
    /wallet/transact?amount=10?to=0x92abcdef0123456789fedcba9876543210

To see the above transaction set in the trasaction pool:
    /txns

After mining a claim, check out the new claims created by the new block by going back to claims route