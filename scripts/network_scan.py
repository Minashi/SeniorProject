import subprocess
import argparse

def perform_scan(scan_type, target, ports=None, protocol='tcp'):
    if scan_type == 'ip':
        if protocol == 'tcp':
            nmap_command = f'nmap -sn {target}'
        elif protocol == 'udp':
            nmap_command = f'nmap -sn -sU {target}'
    elif scan_type == 'ports':
        if protocol == 'tcp':
            nmap_command = f'nmap -p {ports} {target}'
        elif protocol == 'udp':
            nmap_command = f'nmap -p {ports} -sU {target}'
    else:
        print("Invalid scan type. Choose 'ip' for IP range scan or 'ports' for port scan.")
        return

    result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)
    print(result.stdout)

parser = argparse.ArgumentParser(description="Network Scanning")
parser.add_argument("-t", "--target", help="Target IP range or hostname")
parser.add_argument("-s", "--scan_type", choices=['ip', 'ports'], help="Choose 'ip' for IP range scan or 'ports' for port scan")
parser.add_argument("-p", "--ports", default="1-1000", help="Ports to scan (default: 1-1000)")
parser.add_argument("-r", "--protocol", choices=['tcp', 'udp'], default='tcp', help="Specify 'tcp' for TCP scan or 'udp' for UDP scan")

args = parser.parse_args()

target = args.target
scan_type = args.scan_type
ports = args.ports
protocol = args.protocol

perform_scan(scan_type, target, ports, protocol)
