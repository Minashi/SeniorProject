import tkinter as tk
from tkinter import ttk

# Importing functionalities from other modules
from ap_enumeration_gui import access_point_enumeration_gui, list_discovered_aps_gui
from lan_enumeration_gui import enumerate_lan_gui, save_enumeration_results
from network_tools import check_root_user, enable_monitor_mode, run_airodump
from pivot_menu_gui import pivot_menu_gui
from vulnerability_analysis_gui import analyze_vulnerabilities_gui
from wep_cracking_gui import crack_wep_gui

def setup_gui():
    root = tk.Tk()
    root.title("Network Pentesting Framework")
    root.geometry("800x600")

    # Set the default color for the root window which will match ttk buttons
    root.configure(background='light grey')  
    root.resizable(False, False)

    # Create the title frame
    title_frame = tk.Frame(root, bg='light grey')
    title_frame.pack(fill="x")
    title_frame.grid_columnconfigure(0, weight=1)

    # Place the title label
    title_label = tk.Label(title_frame, text="Network Pentesting Framework", bg='light grey', fg='black', font=('Helvetica', 20, 'bold'))
    title_label.grid(row=0, column=0, pady=(10, 20))

    # Create the button frame
    button_frame = tk.Frame(root, bg='light grey')
    button_frame.pack(fill="both", expand=True)
    button_frame.grid_columnconfigure(0, weight=1)

    # Buttons for various functionalities, now using grid layout in the button_frame
    buttons = [
        ("Enumerate Access Points", access_point_enumeration_gui),
        ("List Discovered APs", list_discovered_aps_gui),
        ("Pivot Menu", lambda: pivot_menu_gui(root)),
        ("Enumerate LAN", lambda: enumerate_lan_gui(root)),
        ("Analyze Vulnerabilities", analyze_vulnerabilities_gui),
        ("Crack WEP Encryption", crack_wep_gui),
        ("Enable Monitor Mode", enable_monitor_mode)
    ]

    for i, (text, command) in enumerate(buttons):
        btn = ttk.Button(button_frame, text=text, command=command)
        btn.grid(row=i, column=0, sticky="nsew", padx=20, pady=5)
        button_frame.grid_rowconfigure(i, weight=1)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
