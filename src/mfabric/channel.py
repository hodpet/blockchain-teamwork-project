from mfabric.orderer import Orderer
from mfabric.validator import validate_block

class Channel:
    def __init__(self, name, policy):
        self.name = name
        self.policy = policy
        self.world_state = {}
        self.ledger = []
        self.orderer = Orderer(batch_size=10)

    def submit_transaction(self, tx):
        """Routes a transaction to the channel's orderer."""
        block = self.orderer.submit(tx)
        
        # If the orderer cut a block, validate and commit it to this channel's ledger
        if block:
            validate_block(block, self.world_state, self.policy)
            self.ledger.append(block)
            return block
        return None

    def force_cut_block(self):
        """Forces the orderer to cut a block even if the batch size isn't met."""
        block = self.orderer.cut_block()
        if block:
            validate_block(block, self.world_state, self.policy)
            self.ledger.append(block)
        return block
