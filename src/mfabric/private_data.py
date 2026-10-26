import hashlib

def hash_data(payload):
    """Generates a deterministic SHA-256 hash of the payload for the public ledger."""
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

class PrivateDataCollection:
    def __init__(self, collection_name, authorized_orgs):
        self.collection_name = collection_name
        self.authorized_orgs = set(authorized_orgs)
        self.side_db = {}  # Off-ledger transient storage

    def put(self, requesting_org, key, value):
        """Stores the plaintext locally and returns the hash for the rwset."""
        if requesting_org not in self.authorized_orgs:
            raise PermissionError(f"{requesting_org} is not authorized for {self.collection_name}")
        
        self.side_db[key] = value
        return hash_data(value)

    def get(self, requesting_org, key):
        """Retrieves the plaintext if the organization is a member."""
        if requesting_org not in self.authorized_orgs:
            raise PermissionError(f"{requesting_org} is not authorized for {self.collection_name}")
        
        return self.side_db.get(key)
