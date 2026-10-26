from mfabric.policy import generate_identity, sign_rwset, satisfies
from mfabric.orderer import Orderer

def test_cryptographic_endorsement_policy():
    # Setup identities
    priv_uni = generate_identity("UniOrg")
    priv_min = generate_identity("MinistryOrg")
    generate_identity("EmployerOrg") # Generate but don't use
    
    policy = (2, ["UniOrg", "MinistryOrg", "EmployerOrg"])
    rwset = {"reads": {"a": 1}, "writes": {"b": 2}}
    
    # Valid endorsements
    e1 = {"org": "UniOrg", "rwset": rwset, "sig": sign_rwset(priv_uni, rwset)}
    e2 = {"org": "MinistryOrg", "rwset": rwset, "sig": sign_rwset(priv_min, rwset)}
    
    assert satisfies(policy, [e1, e2]) is True

def test_forged_signature_rejected():
    priv_uni = generate_identity("UniOrg")
    priv_rogue = generate_identity("RogueOrg")
    
    policy = (1, ["UniOrg"])
    rwset = {"reads": {}, "writes": {"grade": "A+"}}
    
    # Rogue tries to forge a UniOrg signature using its own key
    forged_sig = sign_rwset(priv_rogue, rwset)
    e_forged = {"org": "UniOrg", "rwset": rwset, "sig": forged_sig}
    
    assert satisfies(policy, [e_forged]) is False

def test_orderer_block_cutting():
    orderer = Orderer(batch_size=2)
    
    # Submit first tx - no block cut yet
    b1 = orderer.submit({"txid": "1"})
    assert b1 is None
    assert len(orderer.pending_transactions) == 1
    
    # Submit second tx - batch size reached, block should be cut
    b2 = orderer.submit({"txid": "2"})
    assert b2 is not None
    assert len(b2) == 2
    assert len(orderer.blockchain) == 1
    assert len(orderer.pending_transactions) == 0
