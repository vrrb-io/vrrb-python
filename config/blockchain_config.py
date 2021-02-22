import time
import numpy as np
import random
import decimal

GENESIS_DATA = {
    'timestamp': 1, 
    'last_block_hash': 
    'genesis_last_hash', 
    'block_hash': 
    'genesis_hash', 
    'data': [], 
    'difficulty': 1, 
    'nonce': 1}

VRRB_ALPHABET = b'VrRbJSQlk6EKjgdmtf8u9pIHvhsi3DPF1qn2UB7Nca54MLeTACG'
VRRB_TESTNET = {
    'port': 19292,
    'wallet_byte_prefix': b'0x192'
}
VRRB_MAINNET = {
    'port': 9292,
    'wallet_byte_prefix': b'0x92'
}

def decay_calculator(
    initial_amount=100, 
    time=0, 
    final_amount=1):
    """
    Calculate the decay given amount and time
    """
    b = (final_amount/initial_amount)
    ln_b = np.log(b)
    return (ln_b/time)



def weighted_choice(objects, weights):
    """
    Generate the mining reward for a given block

    """
    weights = np.array(weights, dtype=np.float64)
    sum_of_weights = weights.sum()
    np.multiply(weights, 1/sum_of_weights, weights)
    weights = weights.cumsum()
    x = random.random()
    for i in range(len(weights)):
        if x < weights[i]:
            return objects[i]

FLAKE_REWARD = (1, 39)
NUGGET_REWARD = (40, (40**2.) - 1)
VEIN_REWARD = (40**2, (40**3) - 1)
MOTHERLODE_REWARD = (40**3, (40**4))

FLAKES_AVAILABLE = float('inf')

NUGGETS_AVAILABLE = 40000000
VEINS_AVAILABLE = 700000 
MOTHERLODES_AVAILABLE = 10000
YEAR_OF_FINAL_NUGGET = 2300
YEAR_OF_FINAL_VEIN = 2200
YEAR_OF_FINAL_MOTHERLODE = 2100
CURRENT_YEAR = 2021

NUGGET_DECAY = abs(decay_calculator(NUGGETS_AVAILABLE, (YEAR_OF_FINAL_NUGGET - CURRENT_YEAR)))
VEIN_DECAY = abs(decay_calculator(VEINS_AVAILABLE, (YEAR_OF_FINAL_VEIN - CURRENT_YEAR)))
MOTHERLODE_DECAY = abs(decay_calculator(MOTHERLODES_AVAILABLE, (YEAR_OF_FINAL_MOTHERLODE - CURRENT_YEAR)))


NANOSECONDS = 1
MICROSECONDS = 1000 * NANOSECONDS
MILLISECONDS = 1000 * MICROSECONDS
SECONDS = 1000 * MILLISECONDS
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
WEEKS = 7 * DAYS
YEARS = 52 * WEEKS

TRUE_MINE_RATE = 5 * SECONDS 
MINE_RATE = SECONDS / 100
TOTAL_BLOCKS = int((YEARS / TRUE_MINE_RATE))
STARTING_BALANCE = 1000



POTENTIAL_REWARD = {
    'flake': {
        'type': 'flake',
        'amount': FLAKE_REWARD,
        'num_available_overall': FLAKES_AVAILABLE,
        'num_available_curr_year': (TOTAL_BLOCKS - sum([
            round(NUGGETS_AVAILABLE * NUGGET_DECAY),
            round(VEINS_AVAILABLE * VEIN_DECAY),
            round(MOTHERLODES_AVAILABLE * MOTHERLODE_DECAY),
        ])),
        'decay': 0
        }, 
    
    'nugget': {
        'type': 'nugget',
        'amount': NUGGET_REWARD, 
        'num_available_overall': NUGGETS_AVAILABLE,
        'num_available_curr_year': round(NUGGETS_AVAILABLE * NUGGET_DECAY),
        'decay': NUGGET_DECAY
        },
    
    'vein': {
        'type': 'vein',
        'amount': VEIN_REWARD,
        'num_available_overall': VEINS_AVAILABLE,
        'num_available_curr_year': round(VEINS_AVAILABLE * VEIN_DECAY),
        'decay': VEIN_DECAY
        },
    
    'motherlode': {
        'type': 'motherlode',
        'amount': MOTHERLODE_REWARD,
        'num_available_overall': MOTHERLODES_AVAILABLE,
        'num_available_curr_year': round(MOTHERLODES_AVAILABLE * MOTHERLODE_DECAY),
        'decay': MOTHERLODE_DECAY
        }
}

REWARDS_LIST = [
        POTENTIAL_REWARD['motherlode'], 
        POTENTIAL_REWARD['vein'], 
        POTENTIAL_REWARD['nugget'], 
        POTENTIAL_REWARD['flake']
        ]

REWARDS_WEIGHTS = [
        (POTENTIAL_REWARD['motherlode']['num_available_curr_year'] / TOTAL_BLOCKS),
        (POTENTIAL_REWARD['vein']['num_available_curr_year'] / TOTAL_BLOCKS),
        (POTENTIAL_REWARD['nugget']['num_available_curr_year'] / TOTAL_BLOCKS),
        (POTENTIAL_REWARD['flake']['num_available_curr_year'] / TOTAL_BLOCKS)
        ]

def generate_reward_amount(reward_range):
    reward = decimal.Decimal(random.randint(reward_range[0], reward_range[1]))
    reward = f'{str(reward)}.000000000000000000'
    return reward

def generate_reward(reward_list=REWARDS_LIST, reward_weight=REWARDS_WEIGHTS):

    reward = weighted_choice(reward_list, reward_weight)
    if reward['type'] == 'motherlode':
        if reward['num_available_curr_year'] > 0:
            POTENTIAL_REWARD[reward['type']]['num_available_overall'] -= 1
            POTENTIAL_REWARD[reward['type']]['num_available_curr_year'] -= 1
            return generate_reward_amount(reward['amount'])
        else:
            return generate_reward(reward_list, reward_weight)

    elif reward['type'] == 'vein':
        if reward['num_available_curr_year'] > 0:
            POTENTIAL_REWARD[reward['type']]['num_available_overall'] -= 1
            POTENTIAL_REWARD[reward['type']]['num_available_curr_year'] -= 1
            return generate_reward_amount(reward['amount'])
        else:
            return generate_reward(reward_list, reward_weight)

    elif reward['type'] == 'nugget':
        if reward['num_available_curr_year'] > 0:
            POTENTIAL_REWARD[reward['type']]['num_available_overall'] -= 1
            POTENTIAL_REWARD[reward['type']]['num_available_curr_year'] -= 1
            return generate_reward_amount(reward['amount'])
        else:
            return generate_reward(reward_list, reward_weight)
    
    else:
        return generate_reward_amount(reward['amount'])

MINING_REWARD_INPUT = { 'address': '*--official-mining-reward--**', 'timestamp': time.time_ns()}


def main():
    for _ in range(int(TOTAL_BLOCKS)):
        MINING_REWARD = generate_reward(REWARDS_LIST, REWARDS_WEIGHTS)
        if int(decimal.Decimal(MINING_REWARD)) in range(POTENTIAL_REWARD['motherlode']['amount'][0], POTENTIAL_REWARD['motherlode']['amount'][1]):
            print(MINING_REWARD)
            


if __name__ == '__main__':
    main()
