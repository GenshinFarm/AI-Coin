import time
import threading
from blockchain import MCAIBlockchain
from node import MCAINode
from app import MCAIApp

if __name__ == "__main__":
    mcai = MCAIBlockchain(host="localhost", port=5000)
    mcai.add_peer("localhost", 5001)

    for i in range(2):
        node = MCAINode(f"AI_Node_{i+1}", mcai)
        mcai.nodes.append(node)
        threading.Thread(target=node.run, daemon=True).start()

    app = MCAIApp(mcai)