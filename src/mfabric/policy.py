import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# Store public keys for each organization (simulating a basic MSP / PKI)
ORG_DIRECTORY = {}

def generate_identity(org_name):
    """Generates an ECDSA private key for an org and registers its public key."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    ORG_DIRECTORY[org_name] = private_key.public_key()
    return private_key

def serialize_rwset(rwset):
    """Deterministically serializes the read-write set for signing."""
    return json.dumps(rwset, sort_keys=True).encode('utf-8')

def sign_rwset(private_key, rwset):
    """Signs the serialized read-write set."""
    payload = serialize_rwset(rwset)
    return private_key.sign(payload, ec.ECDSA(hashes.SHA256()))

def verify_signature(org, signature, rwset):
    """Verifies that the signature matches the org's public key and the rwset."""
    if org not in ORG_DIRECTORY:
        return False
    public_key = ORG_DIRECTORY[org]
    payload = serialize_rwset(rwset)
    try:
        public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def satisfies(policy, endorsements):
    """
    Evaluates if the endorsements meet the policy threshold.
    Validates unique organizations and cryptographic signatures.
    """
    n, allowed_orgs = policy
    valid_orgs = set()
    
    for e in endorsements:
        org = e["org"]
        if org in allowed_orgs and verify_signature(org, e["sig"], e["rwset"]):
            valid_orgs.add(org)
            
    return len(valid_orgs) >= n
