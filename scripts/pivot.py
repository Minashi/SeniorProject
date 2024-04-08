import os, subprocess
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
        subprocess.run(['nmcli', 'device', 'disconnect', 'wlan0'], check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        print(f"Attempting to connect to Wi-Fi SSID: {ssid}")
        connection_result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if connection_result.returncode == 0:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect to {ssid}: {connection_result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to connect to the Wi-Fi: {e}")
