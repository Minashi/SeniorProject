import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import subprocess
import csv
import os

def access_point_enumeration_gui():
    enumeration_window = tk.Toplevel()
    enumeration_window.title("AP Enumeration Progress")
    log_text = tk.Text(enumeration_window, height=10, width=50)
    log_text.pack(pady=10)

    def update_enumeration_log(process, log_widget):
        for line in iter(process.stdout.readline, ''):
            log_widget.insert(tk.END, line)
            log_widget.see(tk.END)
        process.stdout.close()
        process.wait()

    def run_enumeration():
        cmd = ["airodump-ng", "wlan0mon"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        update_enumeration_log(process, log_text)

    threading.Thread(target=run_enumeration).start()

def list_discovered_aps_gui():
    ap_window = tk.Toplevel()
    ap_window.title("Discovered Access Points")
    ap_window.geometry("800x400")

    columns = ('BSSID', 'Channel', 'Encryption', 'ESSID', 'Signal Strength')
    ap_tree = ttk.Treeview(ap_window, columns=columns, show='headings')

    for col in columns:
        ap_tree.heading(col, text=col)
        ap_tree.column(col, width=150 if col == 'BSSID' else 100)

    csv_file = None
    for file in os.listdir("."):
        if file.startswith("airodump_output") and file.endswith(".csv"):
            csv_file = file
            break

    if csv_file:
        try:
            with open(csv_file, "r") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    ap_tree.insert('', tk.END, values=(
                        row.get('BSSID', 'N/A'),
                        row.get('Channel', 'N/A'),
                        row.get('Privacy', 'N/A'),
                        row.get('ESSID', 'N/A'),
                        row.get('Power', 'N/A')
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse AP data: {e}")
    else:
        messagebox.showerror("Error", "No airodump-ng output file found. Please run enumeration first.")

    scrollbar = ttk.Scrollbar(ap_window, orient=tk.VERTICAL, command=ap_tree.yview)
    ap_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    ap_tree.pack(expand=True, fill='both')

    ap_tree.bind('<Double-1>', on_ap_selected)

def on_ap_selected(event):
    selected_item = event.widget.selection()[0]  # event.widget gives you the treeview
    ssid = event.widget.item(selected_item, 'values')[3]  # Adjust index based on your columns

    password_prompt = f"Enter password for {ssid} (Leave blank to use saved password):"
    password = simpledialog.askstring("Password", password_prompt, parent=event.widget)

    if password is None:  # User cancelled the dialog
        return

    if not password:  # Try to retrieve saved password if user left the prompt blank
        try:
            with open("passwords.txt", "r") as file:
                for line in file:
                    line_ssid, line_password = line.strip().split(',', 1)
                    if line_ssid == ssid:
                        password = line_password
                        break
        except FileNotFoundError:
            messagebox.showerror("Error", "passwords.txt file not found.")
            return

    if not password:
        messagebox.showerror("Error", f"No password provided or found for {ssid}.")
        return

    # Connection attempt
    try:
        connect_command = ["nmcli", "device", "wifi", "connect", ssid, "password", password, "ifname", "wlan0"]
        result = subprocess.run(connect_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        messagebox.showinfo("Connection Attempt", f"Connected to {ssid}\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Connection Attempt", f"Failed to connect to {ssid}\n{e.stderr}")
