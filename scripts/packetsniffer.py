import subprocess

def capture_packets(interface, ip_address, output_file):
    
    tcpdump_command = f"tcpdump -i {interface} -s 0 -n -v -w {output_file} 'host {ip_address}'"

    try:
        # Start tcpdump process
        process = subprocess.Popen(tcpdump_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
        input("Press Enter to stop capturing...")

   
        process.terminate()

        
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'))

    except KeyboardInterrupt:
       
        process.terminate()
        print("Packet capture stopped by user.")


interface = input("Enter interface name: ")
ip_address = input("Enter IP address: ")
output_file = input("Enter output file name (with .pcap extension): ")
capture_packets(interface, ip_address, output_file)
