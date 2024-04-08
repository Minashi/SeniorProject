import subprocess, time, sys, csv, os, re
from prettytable import PrettyTable

from scripts import wep, wps, wpa2, evil_twin, ap_enum, pivot
from scripts import activedirectory, checksum
from scripts import host_discovery, network_scan, enumerate_lan

host_mac = " "

def check_root_user():
    if os.geteuid() != 0:
        print("This script must be run as root. Exiting.")
        sys.exit(1)

def get_current_mac():
    try:
        global host_mac
        output = subprocess.check_output(["macchanger", "-s", "wlan0mon"]).decode("utf-8")
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
        {"label": "Attacking WPA/2", "function": attacking_wpa2},
        {"label": "Pivot", "function": display_pivot},
        {"label": "Analyze Vulnerabilities", "function": wep.identify_wep},
        {"label": "Checksum Verification", "function": checksum.main},
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

    def target_client():
        nonlocal target_c
        print("Verify there is a client connected! Before attempting!\n")
        target_c = wep.target_c(ap_mac)
        print("\nNew Target Client: ", target_c)

    def crack_wep():
        wep.main(target_ap, ap_mac, host_mac, target_c)
    
    submenu_options = [
        {"label": "Identify WEP Targets", "function": wep.identify_wep},
        {"label": "Set Target Access Point", "function": target_accesspoint},
        {"label": "Set Target Client", "function": target_client},
        {"label": "Crack WEP Key", "function": crack_wep},
        {"label": "Return To Main Menu", "function": exit_menu},
    ]

    while True:
        print("\nAttacking WEP:")
        print("Target Access Point:", target_ap)
        print("Target Client:", target_c, "\n")
        
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")

        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Return To Main Menu":
                break
        else:
            print("Invalid option, please try again.")

def attacking_wpa2():
    target_ap = "Not Set"
    target_c = "Not Set"

    def target_accesspoint():
        nonlocal target_ap
        target_ap = wpa2.target_ap()
        print("\nNew Target Access Point: ", target_ap)

    def target_client():
        nonlocal target_c
        target_c = wpa2.target_c()
        print("\nNew Target Client: ", target_c)

    submenu_options = [
        {"label": "Set Target Access Point", "function": target_accesspoint},
        {"label": "Identify Potential Clients", "function": wpa2.identify_clients},
        {"label": "Set Target Client", "function": target_client},
        {"label": "Deauth Client", "function": wpa2.deauth},
        {"label": "Crack WPA2 Handshake", "function": wpa2.crack_handshake},
        {"label": "Return To Main Menu", "function": exit_menu},
    ]

    while True:
        print("\nAttacking WPA2:")
        print("Target Access Point:", target_ap)
        print("Target Client:", target_c, "\n")

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
        {"label": "Enumerate LAN", "function": enumerate_lan},
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
        {"label": "Validate Domain Existence", "function": activedirectory.is_active_directory},
        {"label": "Basic AD Enumeration", "function": activedirectory.basic_ad_enum},
        {"label": "LLMNR Poisoning: Capture Service Hashes", "function": activedirectory.llmnr_poisoning},
        {"label": "List Captured Hashes", "function": activedirectory.list_hashes},
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

def enumerate_lan():
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

# Check if the user is root before proceeding
check_root_user()
print("\nMAKE SURE YOU ENTER MONITORING MODE BEFORE RUNNING SCRIPT\n")

# Capture host mac
current_mac = get_current_mac()
if current_mac:
    print("Current MAC address:", host_mac, "\n")
else:
    print("Failed to get current MAC address.\n") 

# Initiate loading menu
loading_prompt("Initializing menu", ascii_art)
display_menu()
