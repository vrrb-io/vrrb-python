
class ClaimPool:
    def __init__(self):
        self.claim_map = {}
    
    def set_claim(self, claim):
        self.claim_map[claim.maturation_time] = claim

    def update_claim(self, claim):
        self.claim_map[claim.maturation_time] = claim

    def remove_claim(self, claim):
        self.claim_map.pop(claim.maturation_time)
        print(len(self.claim_map.keys()))

    def to_json(self):
        claim_dict = {}
        for i in self.claim_map:
            claim_dict[i] = self.claim_map[i].to_json()
        return claim_dict
