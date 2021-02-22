
class AccountModel:

    def __init__(self):
        self.accounts = []
        self.balances = {}
    
    def add_account(self, address):
        if not address in self.accounts:
            self.accounts.append(address)
            self.balances[address] = 0
    
    def get_balance(self, address):
        if address not in self.accounts:
            self.add_account(address)
        return self.balances[address]
    
    def update_balances(self, address, amount):
        if address not in self.accounts:
            self.add_account(address)
        
        self.balances[address] += amount