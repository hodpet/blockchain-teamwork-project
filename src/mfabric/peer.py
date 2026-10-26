from mfabric.policy import sign_rwset

class SimView:
    def __init__(self, world, rw):
        self.world = world       
        self.rw = rw             

    def get(self, k):
        if k in self.rw["writes"]:
            return self.rw["writes"][k]
        
        value, ver = self.world.get(k, (None, 0))
        self.rw["reads"][k] = ver
        return value

    def put(self, k, v):
        self.rw["writes"][k] = v

def endorse(org, world, chaincode, args, private_key=None):
    rw = {"reads": {}, "writes": {}}
    sim_view = SimView(world, rw)
    
    chaincode(sim_view, *args)
    
    # M2 Fix: Use the peer's private key to cryptographically sign the rwset
    sig = sign_rwset(private_key, rw) if private_key else f"mock_sig_{org}"
    return {"org": org, "rwset": rw, "sig": sig}
