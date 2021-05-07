class AccountModel:

    def __init__(self):
        self.accounts = []
        self.balances = {}
        self.claims = {}
    
    def add_account(self, address, pk_hash):
        if not (address, pk_hash) in self.accounts:
            self.accounts.append((address, pk_hash))
            self.balances[address] = 0
    
    def get_balance(self, address, pk_hash):
        if address not in self.accounts:
            self.add_account(address, pk_hash)
        return self.balances[address]
    
    def update_balances(self, address, pk_hash, amount):
        if (address, pk_hash) not in self.accounts:
            self.add_account(address, pk_hash)
        
        self.balances[address] += amount
    
    def get_claims_owned(self, address, pk_hash):
        if (address, pk_hash) not in self.accounts:
            self.add_account(address, pk_hash)
        return self.claims[address]
    
    def update_claims_owned(self, address, claim):
        if address not in self.claims:
            self.claims[address] = {}

        self.claims[address][claim.maturation_time] = claim.to_json()

    def delete_mined_claim(self, address, claim):
        if address not in self.claims:
            pass

        self.claims[address].pop(claim.maturation_time)
