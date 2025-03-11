import tkinter as tk
from tkinter import messagebox
import json

class MCAIApp:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.root = tk.Tk()
        self.root.title("MCAI Blockchain")
        self.text = tk.Text(self.root, height=20, width=80)
        self.text.pack()
        self.update_ui()
        self.root.mainloop()

    def update_ui(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, "Blockchain:\n")
        for block in self.blockchain.chain[-5:]:
            self.text.insert(tk.END, json.dumps(block.to_dict(), indent=2) + "\n")
        self.text.insert(tk.END, "\nSố dư:\n")
        for user, balance in self.blockchain.balances.items():
            self.text.insert(tk.END, f"{user}: {balance} MCAI\n")
        self.root.after(5000, self.update_ui)