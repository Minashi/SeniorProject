import subprocess, time, sys, csv, os, re, atexit
from prettytable import PrettyTable

from scripts import wep, wps, wpa2, ap_enum, pivot
from scripts import activedirectory, checksum
from scripts import host_discovery, network_scan, enumerate_lan
from scripts.password_utilities import generate_password_interface, test_password_strength_interface

host_mac = " "

class DualLogger:
    def __init__(self, file_path, terminal):
        self.terminal = terminal
        self.log = open(file_path, "a")

    def write(self, message):
        try:
            self.terminal.write(message)
            self.log.write(message)
        except Exception as e:
            pass  # Consider logging this to a file or handling appropriately

    def flush(self):
        try:
            self.terminal.flush()
            self.log.flush()
        except Exception as e:
            pass

    def close(self):
        try:
            if self.log and not self.log.closed:
                self.log.close()
        except Exception as e:
            pass  # Consider how you want to handle a failure to close
    def direct_print(self, message):
        """
        Prints a message directly to the terminal, bypassing the log.
        """
        self.terminal.write(message + "\n")
        self.terminal.flush()

def cleanup():
    # Delegate to the DualLogger's close method
    sys.stdout.direct_print(f"All output has been logged to: {log_path}")
    sys.stdout.close()
    sys.stderr.close()  # If sys.stderr is also a DualLogger

# Set up the dual logging system
log_path = "/mnt/data/log.txt"
sys.stdout = DualLogger(log_path, sys.stdout)
sys.stderr = DualLogger(log_path, sys.stderr)

# Register the cleanup function to be called at exit
atexit.register(cleanup)

def check_root_user():
    if os.geteuid() != 0:
        print("This script must be run as root. Exiting.")
        sys.exit(1)

selected_interface = None

def list_interfaces():
    # List available network interfaces using ip command
    output = subprocess.check_output(["ip", "link"]).decode("utf-8")
    interfaces = re.findall(r'\d+:\s([^:]+):', output)
    
    # Display interfaces for user to choose
    print("Available interfaces:")
    for idx, interface in enumerate(interfaces):
        print(f"{idx + 1}. {interface}")
    
    # Get user choice
    while True:
        try:
            choice = int(input("Choose the interface by number: "))
            if 1 <= choice <= len(interfaces):
                return interfaces[choice - 1]
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a number.")

def monitoring_mode():
    global selected_interface
    selected_interface = list_interfaces()

    # Check if the monitoring interface is already in monitoring mode
    if ap_enum.is_monitor_mode_enabled(selected_interface):
        print(f"Monitoring mode is already enabled on: {selected_interface}\n")
    else:
        print(f"No network adapter is in monitoring mode.")
        user_input = input(f"Would you like to enable monitoring mode on {selected_interface}? (yes/no): ")
        if user_input.lower() == 'yes':
            selected_interface = ap_enum.enable_monitor_mode(selected_interface)
        else:
            print("Exiting without enabling monitoring mode or scanning.")

def get_current_mac():
    global selected_interface, host_mac
    if selected_interface is None:
        print("No interface has been selected for monitoring. Please run monitoring_mode first.")
        return None
    try:
        output = subprocess.check_output(["macchanger", "-s", selected_interface]).decode("utf-8")
        # Extract the current MAC address using regular expression
        host_mac = re.search(r"Current MAC:\s+([\w:]+)", output).group(1)
        return True
    except subprocess.CalledProcessError as e:
        print("Error:", e.output.decode("utf-8"))
        return None

def loading_prompt(message="", art=None):
    if art:
        print(art)
    print(message)
    for _ in range(3):  # Simple loading animation
        print(".", end="", flush=True)
        time.sleep(1)
    print("\n")

# Start up ASCII Art
ascii_art = """
   ___  
  /   \\\\
 /     \\\\
/_______\\\\
\_______/
"""

# NAVIGATION
def exit_menu():
    print("Exiting menu...")

def display_menu():
    menu_options = [
        {"label": "Access Point Enumeration", "function": ap_enum.main},
        {"label": "List Discovered Access Points", "function": ap_enum.discovered_ap},
        {"label": "Clear Discovered Access Points", "function": ap_enum.delete_accesspoints},
        {"label": "Attacking WEP", "function": attacking_wep},
        {"label": "Attacking WPA", "function": attacking_wpa},
        {"label": "Pivot", "function": display_pivot},
        {"label": "Analyze Vulnerabilities", "function": wep.identify_wep},
        {"label": "Checksum Verification", "function": checksum.main},
        {"label": "Password Utilities", "function": display_password_menu},
        {"label": "Exit", "function": exit_menu},
    ]

    while True:
        print("\nMain Menu:")
        for i, option in enumerate(menu_options, start=1):
            print(f"{i}. {option['label']}")

        try:
            choice = int(input("Select an option: "))
            if 1 <= choice <= len(menu_options):
                menu_options[choice - 1]["function"]()
                if menu_options[choice - 1]["label"] == "Exit":
                    break
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting due to Ctrl+C")
            break

def attacking_wep():
    target_ap = "Not Set"
    target_c = "Not Set"
    ap_mac = " "
    
    def target_accesspoint():
        nonlocal target_ap
        nonlocal ap_mac
        target_ap, ap_mac = wep.target_ap()
        print("\nNew Target Access Point: ", target_ap)

    def crack_wep():
        wep.main(ap_mac, selected_interface)
    
    submenu_options = [
        {"label": "Identify WEP Targets", "function": wep.identify_wep},
        {"label": "Set Target Access Point", "function": target_accesspoint},
        {"label": "Crack WEP Key", "function": crack_wep},
        {"label": "Return To Main Menu", "function": exit_menu},
    ]

    while True:
        print("\nAttacking WEP:")
        print("Target Access Point:", target_ap, "\n")
        
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Return To Main Menu":
                break
        else:
            print("Invalid option, please try again.")

def attacking_wpa():
    target_ap = "Not Set"
    target_c = "Not Set"
    ap_mac = " "

    def target_accesspoint():
        nonlocal target_ap
        nonlocal ap_mac
        target_ap, ap_mac = wpa2.target_ap()
        print("\nNew Target Access Point: ", target_ap)

    def capture_wpa2():
        wpa2.main(ap_mac, selected_interface)

    def crackit():
        wpa2.crack(target_ap)
    
    submenu_options = [
        {"label": "Set Target Access Point", "function": target_accesspoint},
        {"label": "Capture WPA Handshake", "function": capture_wpa2},
        {"label": "Crack WPA Handshake", "function": crackit},
        {"label": "Return To Main Menu", "function": exit_menu},
    ]

    while True:
        print("\nAttacking WPA2:")
        print("Target Access Point:", target_ap)

        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Return To Main Menu":
                break
        else:
            print("Invalid option, please try again.")

def display_pivot():
    submenu_options = [
        {"label": "List Cracked Passwords", "function": pivot.submenu_option_1},
        {"label": "Pivot To Access Point", "function": pivot.submenu_option_2},
        {"label": "Enumerate LAN", "function": lan},
        {"label": "Active Directory", "function": display_activedirectory},
        {"label": "Exit Pivot Menu", "function": exit_menu},
    ]

    while True:
        print("\nPivot:")
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Exit Pivot Menu":
                break
        else:
            print("Invalid option, please try again.")

def display_activedirectory():
    submenu_options = [
        {"label": "Basic AD Enumeration", "function": activedirectory.basic_ad_enum},
        {"label": "LLMNR Poisoning: Capture Service Hashes", "function": activedirectory.llmnr_poisoning},
        {"label": "List Captured Hashes", "function": activedirectory.list_hashes},
        {"label": "Crack Hash", "function": activedirectory.crack_ntlmv2},
        {"label": "Return to Pivot Menu", "function": exit_menu},
    ]

    while True:
        print("\nActive Directory:")
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Return to Pivot Menu":
                break
        else:
            print("Invalid option, please try again.")

def lan():
    print("LAN Enumeration Options:")
    lan_options = [
        {"label": "Basic LAN Scan", "function": enumerate_lan.basic_lan_scan},
        {"label": "Scan for Common Vulnerabilities", "function": enumerate_lan.scan_for_vulnerabilities},
        {"label": "Custom Nmap Script Scan", "function": enumerate_lan.custom_nmap_script_scan},
        {"label": "Return to Previous Menu", "function": display_pivot},
    ]

    while True:
        for i, option in enumerate(lan_options, start=1):
            print(f"{i}. {option['label']}")

        choice = input("Select an option: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(lan_options):
                lan_options[choice - 1]["function"]()
                if lan_options[choice - 1]["label"] == "Return to Previous Menu":
                    break
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("Please enter a number.")

def display_password_menu():
    submenu_options = [
        {"label": "Generate a Password", "function": generate_password_interface},
        {"label": "Test Password Strength", "function": test_password_strength_interface},
        {"label": "Return To Main Menu", "function": exit_menu},
    ]
    
    while True:
        print("\nPassword Utilities:")
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Return To Main Menu":
                break
        else:
            print("Invalid option, please try again.")

# Check if the user is root before proceeding
check_root_user()

# Enable Monitoring Mode
monitoring_mode()

# Capture host mac
current_mac = get_current_mac()
if current_mac:
    print("Current MAC address:", host_mac, "\n")
else:
    print("Failed to get current MAC address.\n") 

# Initiate loading menu
loading_prompt("Initializing menu", ascii_art)
display_menu()
