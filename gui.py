#!/usr/bin/env python3
import os
import tkinter as tk
from tkinter import ttk
import subprocess

class PasswordSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Krupp-Stahl Password Manager")
        self.root.geometry("800x600")
        
        self.passwords = self.read_stored_passwords()
        self.password_states = {i: False for i in range(len(self.passwords))}
        
        self.create_table()
        self.root.focus_force()
        self.tree.focus_force()
        self.tree.focus_set()
    def read_stored_passwords(self):
        # Get the directory where gui.py is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        read_script = os.path.join(script_dir, 'read.py')
        
        # Run read.py with absolute path and capture its output
        result = subprocess.run(['python3', read_script], capture_output=True, text=True)
        output = result.stdout
        entries = []
        segments = output.split('||')
        for segment in segments:
            parts = segment.split('|')
            if len(parts) == 3:
                entries.append({
                    "note": parts[0].strip(),
                    "username": parts[1].strip(),
                    "password": parts[2].strip()
                })
        return entries if entries else []
    def create_table(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('note', 'username', 'password', 'show')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('note', text='Note')
        self.tree.heading('username', text='Username')
        self.tree.heading('password', text='Password')
        self.tree.heading('show', text='Show')
        self.tree.column('note', width=150)
        self.tree.column('username', width=200)
        self.tree.column('password', width=150)
        self.tree.column('show', width=50)

        for i, item in enumerate(self.passwords):
            self.tree.insert('', tk.END, values=(
                item['note'],
                item['username'],
                '*' * len(item['password']),
                'show'
            ))

        if self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)

        self.tree.bind('<ButtonRelease-1>', self.handle_click)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)

        self.show_all_state = False
        show_all_btn = ttk.Button(main_frame, text="Show All Passwords", command=self.toggle_all_passwords)
        show_all_btn.pack(side=tk.BOTTOM, pady=10)

    def handle_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        if region == "cell" and column == "#4":  # Show button column
            item = self.tree.selection()[0]
            index = self.tree.index(item)
            self.toggle_password(index)

    def toggle_password(self, index):
        item_id = self.tree.get_children()[index]
        self.password_states[index] = not self.password_states[index]
        if self.password_states[index]:
            password_display = self.passwords[index]['password']
        else:
            password_display = '*' * len(self.passwords[index]['password'])
        self.tree.item(item_id, values=(
            self.passwords[index]['note'],
            self.passwords[index]['username'],
            password_display,
            'show'
        ))

    def toggle_all_passwords(self):
        self.show_all_state = not self.show_all_state
        for i, item_id in enumerate(self.tree.get_children()):
            self.password_states[i] = self.show_all_state
            password_display = self.passwords[i]['password'] if self.show_all_state else '*' * len(self.passwords[i]['password'])
            self.tree.item(item_id, values=(
                self.passwords[i]['note'],
                self.passwords[i]['username'],
                password_display,
                '👁️'
            ))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordSelector()
    app.run()
    self.root.focus_force()
