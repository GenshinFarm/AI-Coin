import hashlib
import time
import threading
import socket
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from block import MCAIBlock

class MCAIBlockchain:
    def __init__(self, host="localhost", port=5000):
        self.chain = []
        self.difficulty = 4
        self.balances = {"System": 1000000}
        self.reward = 10
        self.nodes = []
        self.peers = []
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.transaction_history = []  # Lưu dữ liệu để học
        genesis_block = self.create_genesis_block()
        self.chain.append(genesis_block)
        self.start_server()

        # Khởi tạo mô hình AI
        X = np.array([[10, 1, 2], [20, 2, 3], [5, 1, 1], [15, 3, 2]])
        y = np.array([1, 1, 0, 1])
        self.ai_model = LogisticRegression()
        self.ai_model.fit(X, y)

    def create_genesis_block(self):
        timestamp = time.time()
        data = "Khối đầu tiên của MCAI"
        hash, nonce = self.proof_of_work(0, "0", timestamp, data)
        return MCAIBlock(0, "0", timestamp, data, hash, nonce)

    def calculate_hash(self, index, previous_hash, timestamp, data, nonce):
        value = f"{index}{previous_hash}{timestamp}{data}{nonce}".encode()
        return hashlib.sha256(value).hexdigest()

    def proof_of_work(self, index, previous_hash, timestamp, data):
        nonce = 0
        start_time = time.time()
        while True:
            hash = self.calculate_hash(index, previous_hash, timestamp, data, nonce)
            if hash.startswith("0" * self.difficulty):
                end_time = time.time()
                self.adjust_difficulty(end_time - start_time)
                return hash, nonce
            nonce += 1

    def adjust_difficulty(self, mining_time):
        if mining_time < 10:
            self.difficulty += 1
        elif mining_time > 30:
            self.difficulty = max(1, self.difficulty - 1)
        print(f"Độ khó hiện tại: {self.difficulty}")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data, miner):
        with self.lock:
            previous_block = self.get_latest_block()
            index = previous_block.index + 1
            timestamp = time.time()
            hash, nonce = self.proof_of_work(index, previous_block.hash, timestamp, data)
            new_block = MCAIBlock(index, previous_block.hash, timestamp, data, hash, nonce)
            self.chain.append(new_block)
            self.balances[miner] = self.balances.get(miner, 0) + self.reward
            print(f"Đã thêm khối bởi {miner}. Số dư: {self.balances[miner]} MCAI")
            self.broadcast_block(new_block)
            self.learn_from_transaction(data, success=1)
            return new_block

    def learn_from_transaction(self, data, success):
        try:
            parts = data.split()
            amount = int(parts[2])
            sender = parts[0]
            receiver = parts[4]
            users = ["AI_Node", "Bạn", "Bố", "Grok"]
            sender_idx = users.index(sender) + 1 if sender in users else 0
            receiver_idx = users.index(receiver) + 1 if receiver in users else 0
            self.transaction_history.append([amount, sender_idx, receiver_idx, success])
            if len(self.transaction_history) >= 10:
                X = np.array([t[:3] for t in self.transaction_history])
                y = np.array([t[3] for t in self.transaction_history])
                self.ai_model.fit(X, y)
                print("Đã cập nhật mô hình AI từ giao dịch!")
                self.transaction_history = []
        except:
            print("Không thể học từ giao dịch:", data)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != self.calculate_hash(current.index, current.previous_hash, current.timestamp, current.data, current.nonce):
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        threading.Thread(target=self.handle_clients, args=(server,), daemon=True).start()
        print(f"Server chạy tại {self.host}:{self.port}")

    def handle_clients(self, server):
        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        data = client.recv(4096)
        block = pickle.loads(data)
        with self.lock:
            if block.index == self.get_latest_block().index + 1 and block.previous_hash == self.get_latest_block().hash:
                self.chain.append(block)
                print(f"Nhận khối mới từ {addr}: {block.data}")
        client.close()

    def broadcast_block(self, block):
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer["host"], peer["port"]))
                s.send(pickle.dumps(block))
                s.close()
            except:
                print(f"Không kết nối được với {peer}")

    def add_peer(self, host, port):
        self.peers.append({"host": host, "port": port})