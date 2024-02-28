import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# Ensure the tkinter root window is initialized in your main GUI module
# and passed to these functions if they need to display messages.

def check_root_user():
    """
    Check if the current user is root. Display an error message and exit if not.
    """
    try:
        if os.geteuid() != 0:
            messagebox.showerror("Error", "This script must be run as root.")
            exit(1)
    except AttributeError:
        # os.geteuid() might not be available on Windows, handle it gracefully
        messagebox.showerror("Error", "Root check is not supported on your operating system.")

def enable_monitor_mode(interface='wlan0'):
    """
    Enable monitor mode on a specified wireless interface.
    
    Parameters:
    - interface: The name of the wireless interface to put into monitor mode (default is 'wlan0').
    
    Returns:
    The modified interface name if monitor mode is enabled, or None if an error occurs.
    """
    try:
        check_result = subprocess.run(['iwconfig', interface], capture_output=True, text=True)
        if "Mode:Monitor" in check_result.stdout:
            messagebox.showinfo("Monitor Mode", f"{interface} is already in monitor mode.")
            return interface
        
        subprocess.run(['airmon-ng', 'start', interface], check=True)
        messagebox.showinfo("Monitor Mode", f"Monitor mode enabled on {interface}mon")
        return interface + 'mon'
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Monitor Mode Error", str(e))
        return None

def run_airodump(interface='wlan0mon', output_file="airodump_output"):
    """
    Run airodump-ng on a specified interface to enumerate access points.
    
    Parameters:
    - interface: The name of the wireless interface in monitor mode (default is 'wlan0mon').
    - output_file: The base name for the output file(s) generated by airodump-ng.
    """
    try:
        subprocess.run(['airodump-ng', '-w', output_file, '--output-format', 'csv', interface], check=True, timeout=30)
        messagebox.showinfo("Enumeration", "AP enumeration completed successfully.")
    except subprocess.TimeoutExpired:
        messagebox.showinfo("Enumeration", "AP enumeration stopped after 30 seconds.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Enumeration Error", str(e))

def run_enumeration(root, command=["sleep", "10"]):
    """
    Run a specified enumeration command and update the GUI upon completion.
    
    Parameters:
    - root: The tkinter root window for displaying the status.
    - command: The enumeration command to run as a list.
    """
    try:
        subprocess.run(command, check=True)
        tk.Label(root, text="Enumeration Completed Successfully!", fg="green").pack()
    except subprocess.CalledProcessError as e:
        tk.Label(root, text=f"Enumeration Failed: {e}", fg="red").pack()

# Note: Make sure to pass the correct tkinter root window to functions that require it for displaying messages.
