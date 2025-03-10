import hashlib
import time
import json
import random
import threading
import socket
import pickle
import tkinter as tk
from tkinter import messagebox
import numpy as np
from sklearn.linear_model import LogisticRegression

# Định nghĩa lớp MrAIBlock
class MrAIBlock:
    def __init__(self, index, previous_hash, timestamp, data, hash, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        self.nonce = nonce

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
            "nonce": self.nonce
        }

# Định nghĩa lớp MrAINFT
class MrAINFT:
    def __init__(self, nft_id, owner, metadata):
        self.nft_id = nft_id
        self.owner = owner
        self.metadata = metadata

    def to_dict(self):
        return {
            "nft_id": self.nft_id,
            "owner": self.owner,
            "metadata": self.metadata
        }

# Định nghĩa lớp MrAIBlockchain
class MrAIBlockchain:
    def __init__(self, host="localhost", port=5000):
        self.chain = []
        self.difficulty = 4
        self.balances = {"System": 1000000}
        self.reward = 10
        self.stakes = {}
        self.nfts = {}
        self.proposals = {}
        self.nodes = []
        self.peers = []
        self.host = host
        self.port = port
        self.lock = threading.Lock()
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
        data = "Khối đầu tiên của MrAI"
        hash, nonce = self.proof_of_work(0, "0", timestamp, data)
        return MrAIBlock(0, "0", timestamp, data, hash, nonce)

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
            new_block = MrAIBlock(index, previous_block.hash, timestamp, data, hash, nonce)
            self.chain.append(new_block)
            self.balances[miner] = self.balances.get(miner, 0) + self.reward
            print(f"Đã thêm khối bởi {miner}. Số dư: {self.balances[miner]} MrAI")
            self.broadcast_block(new_block)
            return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != self.calculate_hash(current.index, current.previous_hash, current.timestamp, current.data, current.nonce):
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    # Staking
    def stake(self, user, amount):
        if self.balances.get(user, 0) >= amount:
            self.balances[user] -= amount
            self.stakes[user] = {'amount': amount, 'start_time': time.time()}
            print(f"{user} đã stake {amount} MrAI")
        else:
            print(f"{user} không đủ số dư để stake")

    def unstake(self, user):
        if user in self.stakes:
            stake_info = self.stakes.pop(user)
            staking_time = time.time() - stake_info['start_time']
            reward = stake_info['amount'] * (staking_time / 3600) * 0.01
            self.balances[user] = self.balances.get(user, 0) + stake_info['amount'] + reward
            print(f"{user} đã unstake và nhận {reward} MrAI phần thưởng")

    def get_balance(self, user):
        balance = self.balances.get(user, 0)
        if user in self.stakes:
            balance += self.stakes[user]['amount']
        return balance

    # NFT
    def create_nft(self, owner, metadata):
        nft_id = len(self.nfts) + 1
        nft = MrAINFT(nft_id, owner, metadata)
        self.nfts[nft_id] = nft
        self.add_block(f"Tạo NFT {nft_id} cho {owner}", "System")
        print(f"Đã tạo NFT {nft_id} cho {owner}")

    def transfer_nft(self, nft_id, from_user, to_user):
        if nft_id in self.nfts and self.nfts[nft_id].owner == from_user:
            self.nfts[nft_id].owner = to_user
            self.add_block(f"Chuyển NFT {nft_id} từ {from_user} sang {to_user}", "System")
            print(f"Đã chuyển NFT {nft_id} từ {from_user} sang {to_user}")
        else:
            print("Không thể chuyển NFT")

    # Quản trị cộng đồng
    def create_proposal(self, proposer, description):
        proposal_id = len(self.proposals) + 1
        self.proposals[proposal_id] = {"description": description, "votes": {}, "proposer": proposer}
        self.add_block(f"Tạo đề xuất {proposal_id}: {description}", proposer)
        print(f"Đã tạo đề xuất {proposal_id}")

    def vote(self, proposal_id, voter, vote_value):
        if proposal_id in self.proposals and voter not in self.proposals[proposal_id]["votes"]:
            self.proposals[proposal_id]["votes"][voter] = vote_value
            self.add_block(f"{voter} bỏ phiếu {vote_value} cho đề xuất {proposal_id}", voter)
            print(f"{voter} đã bỏ phiếu cho đề xuất {proposal_id}")

    # P2P
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

# Định nghĩa lớp MrAINode
class MrAINode:
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
            return f"{sender} gửi {amount} MrAI cho {receiver}"
        return None

    def run(self):
        while True:
            transaction = self.generate_transaction()
            if transaction:
                print(f"Node {self.node_id} đào khối: {transaction}")
                self.blockchain.add_block(transaction, self.node_id)
            time.sleep(random.uniform(5, 15))

# Định nghĩa lớp MrAIApp
class MrAIApp:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.root = tk.Tk()
        self.root.title("MrAI Blockchain")
        self.text = tk.Text(self.root, height=20, width=80)
        self.text.pack()

        # Game hóa
        self.game_label = tk.Label(self.root, text="Chơi game để kiếm MrAI: 1+1=?")
        self.game_label.pack()
        self.game_entry = tk.Entry(self.root)
        self.game_entry.pack()
        self.game_button = tk.Button(self.root, text="Trả lời", command=self.check_answer)
        self.game_button.pack()

        self.update_ui()
        self.root.mainloop()

    def update_ui(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "Blockchain:\n")
        for block in self.blockchain.chain[-5:]:
            self.text.insert(tk.END, json.dumps(block.to_dict(), indent=2) + "\n")
        self.text.insert(tk.END, "\nSố dư:\n")
        for user, balance in self.blockchain.balances.items():
            self.text.insert(tk.END, f"{user}: {balance} MrAI\n")
        self.text.insert(tk.END, "\nStaking:\n")
        for user, stake in self.blockchain.stakes.items():
            self.text.insert(tk.END, f"{user}: {stake['amount']} MrAI\n")
        self.text.insert(tk.END, "\nNFTs:\n")
        for nft in self.blockchain.nfts.values():
            self.text.insert(tk.END, json.dumps(nft.to_dict(), indent=2) + "\n")
        self.text.insert(tk.END, "\nProposals:\n")
        for pid, prop in self.blockchain.proposals.items():
            self.text.insert(tk.END, f"{pid}: {prop['description']} - Votes: {len(prop['votes'])}\n")
        self.root.after(5000, self.update_ui)

    def check_answer(self):
        answer = self.game_entry.get()
        if answer == "2":
            self.blockchain.balances["Bạn"] = self.blockchain.balances.get("Bạn", 0) + 5
            messagebox.showinfo("Thành công", "Bạn đã kiếm được 5 MrAI!")
        else:
            messagebox.showerror("Sai", "Sai đáp án!")
        self.game_entry.delete(0, tk.END)

# Chạy ứng dụng
if __name__ == "__main__":
    mrai = MrAIBlockchain(host="localhost", port=5000)
    mrai.add_peer("localhost", 5001)

    # Thêm node AI
    for i in range(2):
        node = MrAINode(f"AI_Node_{i+1}", mrai)
        mrai.nodes.append(node)
        threading.Thread(target=node.run, daemon=True).start()

    # Ví dụ sử dụng các tính năng
    mrai.balances["Bạn"] = 200
    mrai.stake("Bạn", 100)
    time.sleep(5)
    mrai.unstake("Bạn")
    mrai.create_nft("Bạn", "Ảnh kỹ thuật số độc quyền")
    mrai.transfer_nft(1, "Bạn", "Bố")
    mrai.create_proposal("Bạn", "Tăng phần thưởng đào lên 20 MrAI")
    mrai.vote(1, "Bố", "Yes")

    # Chạy giao diện
    app = MrAIApp(mrai)
