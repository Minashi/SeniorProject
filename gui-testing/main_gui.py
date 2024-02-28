import tkinter as tk
from tkinter import ttk

# Importing functionalities from other modules
from ascii_art_gui import display_ascii_art_gui
from ap_enumeration_gui import access_point_enumeration_gui, list_discovered_aps_gui
from lan_enumeration_gui import enumerate_lan_gui, save_enumeration_results
from network_tools import check_root_user, enable_monitor_mode, run_airodump
from pivot_menu_gui import pivot_menu_gui
from vulnerability_analysis_gui import analyze_vulnerabilities_gui
from wep_cracking_gui import crack_wep_gui

def setup_gui():
    root = tk.Tk()
    root.title("Network Security Toolkit")
    root.geometry("800x600")

    style = ttk.Style(root)
    style.theme_use('clam')

    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill="both", expand=True)

    # Buttons for various functionalities
    ttk.Button(main_frame, text="Display ASCII Art", command=lambda: display_ascii_art_gui(root)).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Enumerate Access Points", command=access_point_enumeration_gui).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="List Discovered APs", command=list_discovered_aps_gui).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Pivot Menu", command=lambda: pivot_menu_gui(root)).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Analyze Vulnerabilities", command=analyze_vulnerabilities_gui).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Crack WEP Encryption", command=crack_wep_gui).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Check Root User", command=check_root_user).pack(pady=10, fill='x', expand=True)

    ttk.Button(main_frame, text="Enable Monitor Mode", command=lambda: enable_monitor_mode()).pack(pady=10, fill='x', expand=True)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
