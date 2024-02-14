from prettytable import PrettyTable
import subprocess
import time
import sys
import csv
import os
import re

def check_root_user():
    if os.geteuid() != 0:
        print("This script must be run as root. Exiting.")
        sys.exit(1)

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

# MENU OPTIONS
def menu_option_1():
    def ensure_data_directory_exists():
        directory = "/mnt/data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def is_monitor_mode_enabled(interface):
        try:
            result = subprocess.run(['iwconfig', interface], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            output = result.stdout
            return "Mode:Monitor" in output
        except Exception as e:
            print(f"An error occurred while checking monitoring mode: {e}")
            return False

    def enable_monitor_mode(interface):
        try:
            print(f"Enabling monitoring mode on {interface}...")
            result = subprocess.run(['airmon-ng', 'start', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if is_monitor_mode_enabled(interface + 'mon'):
                print(f"Monitoring mode enabled on {interface}mon")
                return True
            else:
                print("Failed to enable monitoring mode.")
                return False
        except Exception as e:
            print(f"An error occurred while enabling monitoring mode: {e}")
            return False

    def run_airodump(interface):
        try:
            file_prefix = ensure_data_directory_exists() + "/airodump"
            airodump_process = subprocess.Popen(['airodump-ng', '--write', file_prefix, '--output-format', 'csv', interface],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Airodump-ng is running... Press Ctrl+C to stop.")
            try:
                airodump_process.wait()
            except KeyboardInterrupt:
                airodump_process.terminate()
                print("\nAirodump-ng stopped by user.")
            airodump_process.communicate()

            directory = ensure_data_directory_exists()
            csv_file = None
            for file in os.listdir(directory):
                if file.startswith("airodump") and file.endswith('.csv'):
                    csv_file = directory + '/' + file
                    break

            if csv_file is None:
                print("No CSV file generated by airodump-ng.")
                return

            # Initialize a file to write all access points
            all_aps_filename = directory + '/access_points.txt'
            with open(all_aps_filename, 'w') as aps_file:
                # Extract BSSID, ENC, and SSID and write to the single file
                with open(csv_file, mode='r') as file:
                    csv_reader = csv.reader(file)
                    next(csv_reader)  # Skip the initial header row from the source CSV if it exists
                    for row in csv_reader:
                        if len(row) >= 14:  # Ensure the row has enough columns
                            bssid = row[0].strip()
                            enc = row[5].strip()
                            ssid = row[13].strip()
                            if bssid and enc and ssid:  # Check for non-empty values
                                aps_file.write(f"{bssid}, {enc}, {ssid}\n")
                print(f"Extraction complete, all access points saved to {all_aps_filename}")
        except Exception as e:
            print(f"An error occurred: {e}")
            

    def ask_for_scan(interface):
        response = input("Would you like to perform a scan with airodump-ng? (yes/no): ")
        if response.lower() == 'yes':
            run_airodump(interface)
        else:
            print("Exiting without scanning.")

    interface = 'wlan0'
    mon_interface = 'wlan0mon'

    # Check if wlan0mon is already in monitoring mode
    if is_monitor_mode_enabled(mon_interface):
        print(f"Monitoring mode is already enabled on: {mon_interface}")
        ask_for_scan(mon_interface)
    else:
        print("No network adapter is in monitoring mode.")
        user_input = input("Would you like to enable monitoring mode on wlan0? (yes/no): ")
        if user_input.lower() == 'yes':
            if enable_monitor_mode(interface):
                ask_for_scan(mon_interface)
        else:
            print("Exiting without enabling monitoring mode or scanning.")    

def menu_option_2():
    file_path = "/mnt/data/access_points.txt"
    # Initialize the PrettyTable with the specified headers
    table = PrettyTable(["ESSID", "ENC", "BSSID"])
    
    try:
        # Open the file and read the contents using the csv.reader for parsing CSV formatted data
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                bssid, enc, essid = row  # Unpack the row directly into variables
                table.add_row([essid, enc, bssid])  # Add the data to the table
                
        print(table)  # Display the table
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def menu_option_3():
    print("Crack WEP Access Points")
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            wep_enabled_aps = []
            for row in csv_reader:
                if "WEP" in row[1]:  # Assuming the encryption standard is in the second column
                    wep_enabled_aps.append(row)
            if wep_enabled_aps:
                print("WEP Enabled Access Points Found:")
            else:
                print("No access points found using WEP encryption.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while analyzing vulnerabilities: {e}")
    #Attempt to crack the WEP key using aircrack-ng
    for ap_row in wep_enabled_aps:
        ap = ap_row[2]
        print(f"Attempting to crack WEP key for {ap_row}...")
        
        try: #Replace the 2 directories with correct path to rockyou.txt or other wordlist, and the correct path to the packet capture file from airodump
            result = subprocess.run(['sudo', 'aircrack-ng', '-b', ap, '-w', '/mnt/data/rockyou.txt', '/mnt/data/filename.cap'], capture_output = True, text = True)
            if "KEY FOUND" in result.stdout: #Checks the output of the aircrack. If a key was found, store the results.
                password = result.stdout.split("KEY FOUND! [ ")[1].split(" ]")[0]
                ssid = ap 
                # Store cracked passwords
                with open('/mnt/data/passwords.txt', 'a') as f: #Stores any found passwords and associated SSIDs to passwords.txt
                    f.write(f"{ssid},{password}\n")
            else:
                print("Key not found for", ap)
        except Exception as e:
            print("Error occurred:", e)

# PIVOT MENU OPTIONS
def submenu_option_1():
    passwords_file = "/mnt/data/passwords.txt"
    
    # Check if the passwords file exists
    if not os.path.exists(passwords_file):
        print(f"The file {passwords_file} does not exist.")
        return

    # Initialize a PrettyTable with headers
    table = PrettyTable()
    table.field_names = ["Index", "SSID", "Password"]
    
    try:
        with open(passwords_file, 'r') as file:
            ssid_password_pairs = [line.strip().split(',') for line in file if line.strip()]
        
        # Add each SSID and password pair to the table with an index
        for index, (ssid, password) in enumerate(ssid_password_pairs, start=1):
            table.add_row([index, ssid, password])

        print(table)
    
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def submenu_option_2():
    passwords_file = "/mnt/data/passwords.txt"
    ssid_password_pairs = []

    # Read the SSID, Password combinations from the file
    try:
        with open(passwords_file, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    ssid_password_pairs.append((parts[0], parts[1]))
    except FileNotFoundError:
        print(f"The file {passwords_file} was not found.")
        return

    # Display the list of SSIDs to the user
    print("Available networks:")
    for i, (ssid, _) in enumerate(ssid_password_pairs, start=1):
        print(f"{i}. {ssid}")

    # Let the user choose an SSID
    choice = input("Enter the number of the Wi-Fi network you want to connect to: ")
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(ssid_password_pairs):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return

    ssid, password = ssid_password_pairs[choice]

    # Attempt to connect to the selected Wi-Fi network
    try:
        # Disconnect existing Wi-Fi connections to avoid conflicts
        subprocess.run(['nmcli', 'device', 'disconnect', 'wlan0'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"Attempting to connect to Wi-Fi SSID: {ssid}")
        connection_result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if connection_result.returncode == 0:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect to {ssid}: {connection_result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to connect to the Wi-Fi: {e}")
    
def submenu_option_3():
    print("Enumerate LAN")
    enumerate_lan()

# NAVIGATION
def menu_to_submenu():
    print("Entering Main menu...")
    display_submenu()

def exit_menu():
    print("Exiting menu...")

def display_menu():
    # Define menu options here. Add new options by appending to this list.
    menu_options = [
        {"label": "Access Point Enumeration", "function": menu_option_1},
        {"label": "List Discovered Access Points", "function": menu_option_2},
        {"label": "Crack WEP", "function": menu_option_3},
        {"label": "Pivot", "function": menu_to_submenu},
        {"label": "Analyze Vulnerabilities", "function": analyze_vulnerabilities},
        {"label": "Exit", "function": exit_menu},
    ]
    
    while True:
        print("\nMenu:")
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

def display_submenu():
    submenu_options = [
        {"label": "List Cracked Passwords", "function": submenu_option_1},
        {"label": "Pivot To Access Point", "function": submenu_option_2},
        {"label": "Enumerate LAN", "function": submenu_option_3},
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
            
def analyze_vulnerabilities():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            vulnerable_aps = []
            for row in csv_reader:
                if "WEP" in row[1]:  # Assuming the encryption standard is in the second column
                    vulnerable_aps.append(row)
            if vulnerable_aps:
                print("Vulnerable Access Points Found:")
                for ap in vulnerable_aps:
                    print(f"SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")
                    print("Vulnerability: Uses WEP encryption, which is outdated and easily cracked.")
                    print("Remediation: Upgrade to WPA3 or at least WPA2 encryption.\n")
            else:
                print("No vulnerable access points found using WEP encryption.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while analyzing vulnerabilities: {e}")

def enumerate_lan():
    print("LAN Enumeration Options:")
    lan_options = [
        {"label": "Basic LAN Scan", "function": basic_lan_scan},
        {"label": "Scan for Common Vulnerabilities", "function": scan_for_vulnerabilities},
        {"label": "Custom Nmap Script Scan", "function": custom_nmap_script_scan},
        {"label": "Return to Previous Menu", "function": display_submenu},
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

def basic_lan_scan():
    target = input("Enter target IP or range (e.g., 192.168.1.1/24): ")
    print(f"Scanning {target}...")
    try:
        subprocess.run(['nmap', target], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the scan: {e}")

def scan_for_vulnerabilities():
    target = input("Enter target IP or range for vulnerability scan: ")
    print(f"Scanning {target} for common vulnerabilities...")
    try:
        subprocess.run(['nmap', '-sV', '--script=vuln', target], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the vulnerability scan: {e}")

def list_nmap_script_options():
    # List of commonly used Nmap scripts and their descriptions
    nmap_scripts = [
        {"script": "vuln", "description": "General vulnerability scanning"},
        {"script": "smb-vuln-ms17-010", "description": "Check for EternalBlue vulnerability (MS17-010)"},
        {"script": "http-heartbleed", "description": "Test for Heartbleed vulnerability in SSL/TLS"},
        {"script": "smb-vuln-cve-2017-5689", "description": "Check for Intel AMT security vulnerability (CVE-2017-5689)"},
        {"script": "rdp-vuln-ms12-020", "description": "Check for vulnerabilities in Microsoft RDP (CVE-2019-0708)"},
        {"script": "smb-vuln-cve-2020-0796", "description": "Check for SMBGhost vulnerability in SMBv3 (CVE-2020-0796)"},
        {"script": "ssh-vuln-cve-2018-10933", "description": "Check for vulnerability in libssh (CVE-2018-10933)"},
        {"script": "http-title", "description": "Get the title of the web server's default page"},
        {"script": "ssl-enum-ciphers", "description": "Enumerate SSL/TLS ciphers and protocols"},
        {"script": "smb-os-discovery", "description": "Discover OS, computer name, and more over SMB"},
        {"script": "dns-zone-transfer", "description": "Attempt a DNS zone transfer"},
        {"script": "broadcast-dhcp-discover", "description": "Discover DHCP servers in the local network"},
        {"script": "mysql-vuln-cve2012-2122", "description": "Check for MySQL auth bypass vulnerability (CVE-2012-2122)"},
        {"script": "ssh2-enum-algos", "description": "Enumerate SSH protocol 2 algorithms supported by the server"},
    ]

    print("Available Nmap Script Options:")
    for i, script in enumerate(nmap_scripts, start=1):
        print(f"{i}. {script['script']} - {script['description']}")
    
    return nmap_scripts

def custom_nmap_script_scan():
    nmap_scripts = list_nmap_script_options()  # Display script options and get the list
    
    script_choice = input("Select a script by number or enter script name directly: ")
    try:
        script_choice = int(script_choice) - 1
        script = nmap_scripts[script_choice]['script']
    except ValueError:
        script = script_choice

    # Display information about the vulnerability associated with the selected script
    if script in vulnerabilities_info:
        vuln_info = vulnerabilities_info[script]
        print(f"\nSelected Script: {script}")
        print(f"Vulnerability Name: {vuln_info['name']}")
        print(f"Description: {vuln_info['description']}")
        print(f"Remediation: {vuln_info['remediation']}\n")
    else:
        print(f"\nSelected Script: {script}")
        print("No specific vulnerability information available for this script.\n")

    # Confirm with the user to proceed with the scan
    proceed = input("Proceed with the scan? (yes/no): ").lower()
    if proceed != 'yes':
        print("Scan cancelled.")
        return

    target = input("Enter target IP or range for custom Nmap script scan: ")
    print(f"\nRunning Nmap script ({script}) on {target}...")
    try:
        result = subprocess.run(['nmap', '--script', script, target], capture_output=True, text=True, check=True)
        print("Scan complete.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the custom script scan: {e}")

vulnerabilities_info = {
    "smb-vuln-ms17-010": {
        "name": "EternalBlue MS17-010",
        "description": "Allows remote code execution due to improper handling of SMB packets.",
        "remediation": "Apply the MS17-010 security update."
    },
    "http-heartbleed": {
        "name": "Heartbleed",
        "description": "A serious vulnerability in the OpenSSL cryptographic software library, allowing attackers to read the memory of servers running vulnerable versions of OpenSSL.",
        "remediation": "Update OpenSSL to version 1.0.1g or later, or recompile OpenSSL without the heartbeat option."
    },
    "smb-vuln-cve-2017-5689": {
        "name": "Intel AMT CVE-2017-5689",
        "description": "A vulnerability in some Intel Active Management Technology, Intel Small Business Technology, and Intel Standard Manageability allows unprivileged network attacker to gain system privileges.",
        "remediation": "Apply Intel firmware updates and check vendor advisories for specific patching instructions."
    },
    "rdp-vuln-ms12-020": {
        "name": "MS12-020 RDP Vulnerability",
        "description": "A pair of vulnerabilities in Microsoft's implementation of the Remote Desktop Protocol (RDP) could allow remote code execution.",
        "remediation": "Install the updates provided by Microsoft in the MS12-020 bulletin."
    },
    "smb-vuln-cve-2020-0796": {
        "name": "SMBGhost",
        "description": "A vulnerability in the Microsoft Server Message Block 3.1.1 (SMBv3) protocol could allow for remote code execution.",
        "remediation": "Apply the update provided by Microsoft addressing this vulnerability (KB4551762)."
    },
    "ssh-vuln-cve-2018-10933": {
        "name": "libssh Authentication Bypass",
        "description": "A vulnerability in libssh could allow an attacker to successfully bypass authentication procedures without any valid credentials.",
        "remediation": "Update the libssh library to version 0.7.6 or later."
    },
    "mysql-vuln-cve2012-2122": {
        "name": "MySQL Auth Bypass CVE-2012-2122",
        "description": "A vulnerability in MySQL and MariaDB that allows an attacker to authenticate as any user if they attempt enough times, due to a flaw in the password checking algorithm.",
        "remediation": "Update MySQL and MariaDB installations to a version that has fixed this vulnerability. For MySQL, versions 5.1.63, 5.5.25, 5.6.7 and later include the fix."
    },
    # The following entries are placeholders. You should fill them in based on the script's purpose and known vulnerabilities it detects.
    "http-title": {
        "name": "Web Server Title Disclosure",
        "description": "Discloses the title of the web server's default page, which could provide sensitive information.",
        "remediation": "Review the web server configuration to limit information disclosure in titles and headers."
    },
    "ssl-enum-ciphers": {
        "name": "Weak SSL/TLS Ciphers Enumeration",
        "description": "Enumerates supported SSL/TLS ciphers and protocols, identifying weak cryptographic standards.",
        "remediation": "Configure the server to use strong ciphers and disable weak ones. Prefer TLS 1.2 or higher."
    },
    "smb-os-discovery": {
        "name": "SMB OS and NetBIOS Information Discovery",
        "description": "Discloses information about the operating system and NetBIOS over SMB, potentially revealing sensitive details.",
        "remediation": "Limit SMB exposure to trusted networks and configure firewalls to block unauthorized SMB traffic."
    },
    "dns-zone-transfer": {
        "name": "DNS Zone Transfer",
        "description": "Attempts to perform a DNS zone transfer which could disclose all the DNS records for a domain.",
        "remediation": "Restrict zone transfers to authorized DNS servers and configure DNS servers securely."
    },
    "broadcast-dhcp-discover": {
        "name": "DHCP Server Discovery",
        "description": "Discovers DHCP servers on the local network, which could reveal unauthorized DHCP services.",
        "remediation": "Ensure only authorized DHCP servers are operational and monitor for rogue DHCP server presence."
    },
    "ssh2-enum-algos": {
        "name": "SSH Algorithms Enumeration",
        "description": "Enumerates supported SSH algorithms, potentially identifying weak algorithms allowed by the server.",
        "remediation": "Configure SSH servers to use strong encryption algorithms and disable weak ones."
    },
}

# Check if the user is root before proceeding
check_root_user()

# Initiate loading menu
loading_prompt("Initializing menu", ascii_art)
display_menu()
