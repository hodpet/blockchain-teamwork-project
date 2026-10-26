class Orderer:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.pending_transactions = []
        self.blockchain = []

    def submit(self, tx):
        """Accepts an endorsed transaction and adds it to the pending pool."""
        self.pending_transactions.append(tx)
        
        # Cut a block if the batch size is reached
        if len(self.pending_transactions) >= self.batch_size:
            return self.cut_block()
        return None

    def cut_block(self):
        """Cuts a block from pending transactions and appends it to the chain."""
        if not self.pending_transactions:
            return None
            
        block = self.pending_transactions.copy()
        self.pending_transactions.clear()
        self.blockchain.append(block)
        
        return block
