import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import subprocess
import threading
import csv
import xml.etree.ElementTree as ET

def enumerate_lan_gui(root):
    lan_window = tk.Toplevel(root)
    lan_window.title("LAN Enumeration Results")
    lan_window.geometry("800x600")

    scan_type_var = tk.StringVar(value="Quick Scan (-sn)")
    scan_options = ["Quick Scan (-sn)", "Port Scan (-p-)", "OS Detection (-O)", "Version Detection (-sV)", "Aggressive Scan (-A)"]

    tk.Label(lan_window, text="Select Scan Type:").pack(pady=(5, 0))
    scan_type_menu = ttk.OptionMenu(lan_window, scan_type_var, *scan_options)
    scan_type_menu.pack()

    # IP Address / Range Input
    tk.Label(lan_window, text="IP Address/Range:").pack(pady=(5, 0))
    ip_entry = ttk.Entry(lan_window)
    ip_entry.pack(pady=(0, 10))
    ip_entry.insert(0, "192.168.1.0/24")  # Default value or example

    columns = ('IP Address', 'Hostname', 'State', 'Ports', 'OS')
    lan_tree = ttk.Treeview(lan_window, columns=columns, show='headings')
    for col in columns:
        lan_tree.heading(col, text=col)
        lan_tree.column(col, anchor="w", width=120 if col == 'IP Address' else 160)

    scrollbar = ttk.Scrollbar(lan_window, orient="vertical", command=lan_tree.yview)
    lan_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    lan_tree.pack(expand=True, fill="both")

    scan_button = ttk.Button(lan_window, text="Start Scan", command=lambda: start_lan_scan(scan_type_var.get(), lan_tree, ip_entry.get()))
    scan_button.pack(pady=(10, 0))

    save_results_button = ttk.Button(lan_window, text="Save Results", command=lambda: save_enumeration_results(lan_tree))
    save_results_button.pack(pady=10)

def start_lan_scan(scan_type, lan_tree, ip_address):
    threading.Thread(target=lambda: run_lan_enumeration(scan_type, lan_tree, ip_address), daemon=True).start()

def run_lan_enumeration(scan_type, lan_tree, ip_address):
    cmd = ["nmap", "-oX", "-", ip_address]  # Use the ip_address from the input field
    if scan_type == "Quick Scan (-sn)":
        cmd.extend(["-sn"])
    elif scan_type == "Port Scan (-p-)":
        cmd.extend(["-p-"])
    elif scan_type == "OS Detection (-O)":
        cmd.extend(["-O"])
    elif scan_type == "Version Detection (-sV)":
        cmd.extend(["-sV"])
    elif scan_type == "Aggressive Scan (-A)":
        cmd.extend(["-A"])

    try:
        nmap_proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parse_nmap_output(nmap_proc.stdout, lan_tree)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Enumeration Error", f"Failed to enumerate LAN: {e.stderr}")

def parse_nmap_output(xml_output, lan_tree):
    try:
        root = ET.fromstring(xml_output)
        for host in root.findall("./host"):
            ip_address = host.find("address[@addrtype='ipv4']").get("addr")
            hostname_element = host.find("hostnames/hostname")
            hostname = hostname_element.get("name") if hostname_element is not None else "N/A"
            state = host.find("status").get("state")

            ports = []
            for port in host.findall("ports/port"):
                port_id = port.get("portid")
                service = port.find("service").get("name") if port.find("service") is not None else "N/A"
                ports.append(f"{port_id}/{service}")

            os_element = host.find("os/osmatch")
            os_name = os_element.get("name") if os_element is not None else "N/A"

            lan_tree.insert("", "end", values=(ip_address, hostname, state, ", ".join(ports), os_name))
    except ET.ParseError as e:
        messagebox.showerror("Parsing Error", "Failed to parse nmap output.")

def save_enumeration_results(tree):
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if not filename:
        return
    with open(filename, "w", newline='') as file:
        writer = csv.writer(file)
        headers = [tree.heading(col)['text'] for col in tree['columns']]
        writer.writerow(headers)
        for item in tree.get_children():
            row = tree.item(item, 'values')
            writer.writerow(row)
    messagebox.showinfo("Save Successful", "LAN enumeration results saved successfully.")

