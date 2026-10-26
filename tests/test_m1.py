from mfabric.peer import endorse
from mfabric.validator import validate_block
from mfabric.policy import generate_identity

# Generate cryptographic identities so M1 tests pass the M2 validator
priv_uni = generate_identity("UniOrg")
generate_identity("MinistryOrg")
generate_identity("EmployerOrg")

def mock_chaincode_transfer(sim_view, key_from, key_to, amount):
    val_from = sim_view.get(key_from) or 0
    val_to = sim_view.get(key_to) or 0
    sim_view.put(key_from, val_from - amount)
    sim_view.put(key_to, val_to + amount)

def test_simulation_does_not_mutate_world():
    world = {"a": (100, 1)}
    
    endorsement = endorse("UniOrg", world, mock_chaincode_transfer, ["a", "b", 10], priv_uni)
    
    assert world == {"a": (100, 1)}
    assert endorsement["rwset"]["writes"] == {"a": 90, "b": 10}
    assert endorsement["rwset"]["reads"] == {"a": 1, "b": 0}

def test_mvcc_read_conflict_and_invalid_tx_retention():
    world = {"intern/42": ("pending", 1)}
    policy = (1, ["UniOrg"])

    def mock_cc_approve(sim_view, key):
        sim_view.get(key)
        sim_view.put(key, "approved")

    e1 = endorse("UniOrg", world, mock_cc_approve, ["intern/42"], priv_uni)
    e2 = endorse("UniOrg", world, mock_cc_approve, ["intern/42"], priv_uni)

    block = [
        {"endorsements": [e1]},
        {"endorsements": [e2]}
    ]

    validate_block(block, world, policy)

    assert block[0]["code"] == "VALID"
    assert block[1]["code"] == "MVCC_READ_CONFLICT"
    
def test_endorsement_org_counting():
    world = {}
    policy = (2, ["UniOrg", "MinistryOrg", "EmployerOrg"])
    
    def mock_cc_noop(sim_view):
        pass

    e1 = endorse("UniOrg", world, mock_cc_noop, [], priv_uni)
    e2 = endorse("UniOrg", world, mock_cc_noop, [], priv_uni)
    
    block = [{"endorsements": [e1, e2]}]
    validate_block(block, world, policy)
    
    assert block[0]["code"] == "ENDORSEMENT_POLICY_FAILURE"
