import subprocess
import argparse
# DISCLAIMER: This uses NMAP, use on networks you have authorization to test on.

# option -aH performs nmap's -sn target ip. Produces active host IP and MAC ADDRESS.

network = "0"
def perform_network_scan(network):
    nmap_command = f'nmap -sn {network}'
    # airodump-ng for access point enumeration
    result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)
    print(result.stdout)


pars = argparse.ArgumentParser(description="Active Host Discovery")
pars.add_argument("-aH", "--activehosts", required=True, help="Use CIDR notation: 192.168.1.0/24)")
args = pars.parse_args()
activehosts = args.activehosts

# user must execute: "sudo python active_host_discovery.py -aH <192.168.1.0/24>", change ip for the network you want.
perform_network_scan(activehosts)



