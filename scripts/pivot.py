import os, subprocess, time, netifaces
from prettytable import PrettyTable

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


def list_network_interfaces():
    """List all network interfaces."""
    interfaces = netifaces.interfaces()
    print("Available network interfaces:")
    for index, interface in enumerate(interfaces, start=1):
        print(f"{index}. {interface}")
    return interfaces

def choose_network_interface():
    """Allow the user to select a network interface."""
    interfaces = list_network_interfaces()
    choice = input("Enter the number of the network interface you want to use: ")
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(interfaces):
            raise ValueError
        return interfaces[choice]
    except ValueError:
        print("Invalid selection. Please enter a valid number.")
        return None

def submenu_option_2():
    interface = choose_network_interface()
    if interface is None:
        return  # Stop if no valid interface is selected

    # Check if the interface is in monitor mode (typically indicated by 'mon' in its name)
    if 'mon' in interface:
        print(f"Interface {interface} appears to be in monitor mode. Attempting to disable monitor mode...")
        try:
            # Use airmon-ng to stop monitor mode on the selected interface
            disable_monitor_mode = subprocess.run(['sudo', 'airmon-ng', 'stop', interface], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Monitor mode disabled: {disable_monitor_mode.stdout.decode()}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to disable monitor mode: {e}")
            return

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

    # Create configuration file for wpa_supplicant
    config_content = f"""
network={{
    ssid="{ssid}"
    key_mgmt=NONE
    wep_key0={password}
    wep_tx_keyidx=0
    scan_ssid=1
}}
"""
    config_path = "/mnt/data/pivot.conf"
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

    log_path = "/mnt/data/pivot.log"

    # Check if log file exists, create if it does not
    if not os.path.exists(log_path):
        open(log_path, 'a').close()

    # Attempt to connect to the selected Wi-Fi network
    try:
        # Kill existing wpa_supplicant processes to avoid conflicts
        subprocess.run(['pkill', 'wpa_supplicant'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start wpa_supplicant and redirect output to log file
        print(f"Attempting to connect to Wi-Fi SSID: {ssid} using wpa_supplicant on {interface}")
        with open(log_path, "a") as log_file:
            subprocess.Popen(['wpa_supplicant', '-Dnl80211', '-i', interface, '-c', config_path], stdout=log_file, stderr=subprocess.STDOUT)

        # Wait for wpa_supplicant to establish connection
        time.sleep(5)  # Wait 5 seconds to ensure wpa_supplicant has time to connect

        # Run dhclient to get an IP address, also redirected to log
        print("Running dhclient to obtain an IP address...")
        with open(log_path, "a") as log_file:
            dhclient_result = subprocess.run(['dhclient', interface, '-v'], stdout=log_file, stderr=subprocess.STDOUT)

        if dhclient_result.returncode == 0:
            print("Successfully connected to the network and IP address assigned.")
        else:
            print("Failed to assign an IP address:", dhclient_result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to connect to the Wi-Fi: {e}")
