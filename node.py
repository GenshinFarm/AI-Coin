import random
import time
import numpy as np

class MCAINode:
    def __init__(self, node_id, blockchain):
        self.node_id = node_id
        self.blockchain = blockchain

    def generate_transaction(self):
        users = ["AI_Node", "Bạn", "Bố", "Grok"]
        sender = random.choice(users)
        receiver = random.choice(users)
        while sender == receiver:
            receiver = random.choice(users)
        amount = random.randint(1, 100)
        prediction = self.blockchain.ai_model.predict(np.array([[amount, users.index(sender) + 1, users.index(receiver) + 1]]))
        if prediction[0] == 1:
            return f"{sender} gửi {amount} MCAI cho {receiver}"
        else:
            self.blockchain.learn_from_transaction(f"{sender} gửi {amount} MCAI cho {receiver}", success=0)
            return None

    def run(self):
        while True:
            transaction = self.generate_transaction()
            if transaction:
                print(f"Node {self.node_id} đào khối: {transaction}")
                self.blockchain.add_block(transaction, self.node_id)
            time.sleep(random.uniform(5, 15))