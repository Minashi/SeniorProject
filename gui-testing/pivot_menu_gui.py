import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import subprocess
import csv
try:
    import pyperclip  # Ensure pyperclip is installed or handle its absence gracefully
except ImportError:
    pyperclip = None

# Assuming enumerate_lan_gui is defined in another module, you would import it here
# from lan_enumeration_gui import enumerate_lan_gui

def pivot_menu_gui(root):
    pivot_window = tk.Toplevel(root)
    pivot_window.title("Pivot Menu")
    pivot_window.geometry("300x200")

    list_cracked_passwords_button = ttk.Button(pivot_window, text="List Cracked Passwords", command=lambda: list_cracked_passwords_gui(pivot_window))
    list_cracked_passwords_button.pack(pady=10)

    pivot_to_access_point_button = ttk.Button(pivot_window, text="Pivot To Access Point", command=lambda: pivot_to_access_point_gui(pivot_window))
    pivot_to_access_point_button.pack(pady=10)

    # Assuming enumerate_lan_gui is correctly imported from its module
    # enumerate_lan_button = ttk.Button(pivot_window, text="Enumerate LAN", command=lambda: enumerate_lan_gui(pivot_window))
    # enumerate_lan_button.pack(pady=10)

def pivot_to_access_point_gui(parent_window):
    pivot_window = tk.Toplevel(parent_window)
    pivot_window.title("Pivot To Access Point")
    pivot_window.geometry("300x200")

    ssid_password_pairs = []
    try:
        with open("passwords.txt", "r") as file:
            ssid_password_pairs = [line.strip().split(',') for line in file.readlines()]
    except FileNotFoundError:
        messagebox.showerror("Error", "passwords.txt file not found.", parent=pivot_window)
        return

    if not ssid_password_pairs:
        messagebox.showinfo("Info", "No saved SSID-password pairs found.", parent=pivot_window)
        return

    ttk.Label(pivot_window, text="Select SSID:").pack()

    ssid_var = tk.StringVar(pivot_window)
    ssid_dropdown = ttk.OptionMenu(pivot_window, ssid_var, *(pair[0] for pair in ssid_password_pairs))
    ssid_dropdown.pack()

    def attempt_connection():
        ssid = ssid_var.get()
        password = next((pair[1] for pair in ssid_password_pairs if pair[0] == ssid), '')
        if not password and pyperclip:
            password = pyperclip.paste()

        if not password:
            password = simpledialog.askstring("Password", f"Enter password for {ssid}:", parent=pivot_window)
        
        if password:
            try:
                result = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password, "ifname", "wlan0"], capture_output=True, text=True, check=True)
                messagebox.showinfo("Connection Successful", f"Successfully connected to {ssid}.\n{result.stdout}", parent=pivot_window)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Connection Error", f"Failed to connect to {ssid}.\n{e.stderr}", parent=pivot_window)

    connect_button = ttk.Button(pivot_window, text="Connect", command=attempt_connection)
    connect_button.pack(pady=10)

def list_cracked_passwords_gui(parent_window):
    passwords_window = tk.Toplevel(parent_window)
    passwords_window.title("Cracked Passwords")
    ttk.Label(passwords_window, text="Double-click a password to use it for connection.").pack()

    columns = ('SSID', 'Password')
    password_tree = ttk.Treeview(passwords_window, columns=columns, show='headings')

    for col in columns:
        password_tree.heading(col, text=col)
        password_tree.column(col, width=150)

    try:
        with open("passwords.txt", "r") as file:
            for line in file:
                ssid, password = line.strip().split(',', 1)
                password_tree.insert('', tk.END, values=(ssid, password))
    except FileNotFoundError:
        messagebox.showerror("Error", "passwords.txt file not found.", parent=passwords_window)

    password_tree.pack(expand=True, fill='both')

    def on_password_selected(event):
        if pyperclip:
            selected_item = password_tree.selection()[0]
            _, password = password_tree.item(selected_item, 'values')
            pyperclip.copy(password)
            messagebox.showinfo("Info", "Password copied to clipboard. Ready to connect.", parent=passwords_window)

    password_tree.bind('<Double-1>', on_password_selected)
