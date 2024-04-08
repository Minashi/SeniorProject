import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Network Scanner using nmap")
    parser.add_argument("targets", help="IP address(es) or hostname(s) to scan")
    parser.add_argument("-sn", action='store_true', help="Host discovery only (Ping Scan)")
    parser.add_argument("-sL", action='store_true', help="List Scan (List Targets)")
    parser.add_argument("-Pn", action='store_true', help="Port scan only")
    parser.add_argument("-PS", action='store_true', help="TCP SYN discovery")
    parser.add_argument("-PA", action='store_true', help="TCP ACK discovery")
    parser.add_argument("-PU", action='store_true', help="UDP discovery")
    parser.add_argument("-PR", action='store_true', help="ARP discovery on local network")
    parser.add_argument("-f", action='store_true', help="Fragment packets")
    parser.add_argument("-D", nargs='+', metavar='decoy_ip', help="Specify decoy IP addresses")
    args = parser.parse_args()

    scan_option = ""
    if args.sL:
        scan_option = "-sL"
    elif args.sn:
        scan_option = "-sn"
    elif args.Pn:
        scan_option = "-Pn"
    elif args.PS:
        scan_option = "-PS"
    elif args.PA:
        scan_option = "-PA"
    elif args.PU:
        scan_option = "-PU"
    elif args.PR:
        scan_option = "-PR"
    elif args.f:
        scan_option = "-f"

    if args.D:
        decoy_ips = " ".join(args.D)
        scan_option += f" -D {decoy_ips}"

    if not scan_option:
        print("Please specify one of the scan options: -sL, -sn, -Pn, -PS, -PA, -PU, -PR, -f")
        return

    command = ["nmap", scan_option] + args.targets.split()
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    main()
