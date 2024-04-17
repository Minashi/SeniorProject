import subprocess

def capture_packets(interface, ip_address, output_file):
    # Ensure the output file is within /mnt/data/
    output_file_path = f"/mnt/data/{output_file}"

    # Construct the tcpdump command
    tcpdump_command = f"tcpdump -i {interface} -s 0 -n -v -w {output_file_path} 'host {ip_address}'"

    try:
        # Start tcpdump process
        process = subprocess.Popen(tcpdump_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Capturing packets on interface {interface} for host {ip_address}.")
        print("Press Enter to stop capturing...")
        input()

        # Stop the process after capturing
        process.terminate()

        # Wait for the process to complete and gather any final output
        stdout, stderr = process.communicate()
        
        # Output the process' stdout and stderr
        print(stdout.decode('utf-8'))
        if stderr:
            print(stderr.decode('utf-8'))

        # Notify user where the output has been saved
        print(f"Packet capture complete. Data has been saved to {output_file_path}")

    except KeyboardInterrupt:
        # Handle user interrupt, terminate subprocess
        process.terminate()
        print("Packet capture stopped by user.")

def packet_sniffer():
    interface = input("Enter the network interface for packet capturing: ")
    ip_address = input("Enter the IP address to filter by (leave empty for no filter): ")
    output_file = input("Enter the filename for captured packets (will be saved in /mnt/data/): ")
    capture_packets(interface, ip_address, f"{output_file}.pcap")

if __name__ == "__main__":
    # Any testing or direct execution code should go here.
    packet_sniffer()
