from mfabric.policy import satisfies

def validate_block(block, world, policy):
    for tx in block:
        # 1. Check endorsement policy using the imported cryptographic version
        if not satisfies(policy, tx["endorsements"]):
            tx["code"] = "ENDORSEMENT_POLICY_FAILURE"
            continue
        
        # 2. Check for non-deterministic execution (divergent rw-sets)
        base_rw = tx["endorsements"][0]["rwset"]
        if any(e["rwset"] != base_rw for e in tx["endorsements"]):
            tx["code"] = "DIVERGENT_RW_SETS"
            continue

        # 3. MVCC Read Validation
        ok = True
        for k, ver in base_rw["reads"].items():
            if world.get(k, (None, 0))[1] != ver:
                ok = False
                break
        
        # 4. Mark transaction status
        tx["code"] = "VALID" if ok else "MVCC_READ_CONFLICT"
        
        # 5. Commit Phase (Apply writes only if valid)
        if ok:
            for k, v in base_rw["writes"].items():
                world[k] = (v, world.get(k, (None, 0))[1] + 1)
