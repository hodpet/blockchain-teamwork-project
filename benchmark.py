import random
import time
from mfabric.policy import generate_identity
from mfabric.peer import endorse
from mfabric.channel import Channel

# 1. Setup Network and Identities
priv_uni = generate_identity("UniOrg")
channel = Channel("internships", policy=(1, ["UniOrg"]))

def mock_cc_update(sim_view, key, val):
    sim_view.get(key)
    sim_view.put(key, val)

def run_benchmark(hot_key_fraction, total_txs=1000):
    # Reset channel state for the run
    channel.world_state = {"hot_key": ("init", 1)}
    channel.ledger = []
    
    transactions = []
    
    # 2. Generate Workload
    for i in range(total_txs):
        if random.random() < hot_key_fraction:
            target_key = "hot_key"
        else:
            target_key = f"unique_key_{i}"
            channel.world_state[target_key] = ("init", 1)
            
        # Endorse tx
        tx = endorse("UniOrg", channel.world_state, mock_cc_update, [target_key, "updated"], priv_uni)
        transactions.append({"endorsements": [tx]})
        
    # 3. Process Workload
    start_time = time.time()
    for tx in transactions:
        channel.submit_transaction(tx)
    channel.force_cut_block()
    duration = time.time() - start_time
    
    # 4. Analyze Results
    valid_count = 0
    conflict_count = 0
    
    for block in channel.ledger:
        for tx in block:
            if tx.get("code") == "VALID":
                valid_count += 1
            elif tx.get("code") == "MVCC_READ_CONFLICT":
                conflict_count += 1
                
    throughput = valid_count / duration if duration > 0 else 0
    return valid_count, conflict_count, throughput

# Run the sweep
fractions = [0.0, 0.1, 0.5, 0.9]
print(f"{'Hot Key %':<10} | {'Valid':<6} | {'Conflicts':<9} | {'Throughput (TPS)':<15}")
print("-" * 47)

for frac in fractions:
    v, c, tps = run_benchmark(frac)
    print(f"{frac*100:>8.0f}% | {v:<6} | {c:<9} | {tps:<15.2f}")
