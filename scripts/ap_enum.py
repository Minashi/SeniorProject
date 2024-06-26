import csv, subprocess, os, sys, signal, re
from prettytable import PrettyTable

def ensure_data_directory_exists():
    directory = "/mnt/data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def is_monitor_mode_enabled(interface):
    try:
        result = subprocess.run(['iwconfig', interface], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        output = result.stdout
        # Check if 'Mode:Monitor' is present in the output
        return "Mode:Monitor" in output
    except Exception as e:
        print(f"An error occurred while checking monitoring mode: {e}")
        return False

def enable_monitor_mode(interface):
    try:
        print(f"Enabling monitoring mode on {interface}...")
        # Run airmon-ng to enable monitoring mode
        result = subprocess.run(['airmon-ng', 'start', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Look for the creation of a monitoring interface in the output
        # Assuming that the new interface is usually named as {interface}mon (as it's the most common pattern)
        mon_interface = f"{interface}mon"
        # Confirm if the new interface is correctly in monitoring mode
        if is_monitor_mode_enabled(mon_interface):
            print(f"Monitoring mode enabled on {mon_interface}\n")
            return mon_interface
        else:
            print(f"Failed to enable monitoring mode on {mon_interface}.\n")
            return False
    except Exception as e:
        print(f"An error occurred while enabling monitoring mode: {e}")
        return False

def run_airodump(interface):
    try:
        # Ensure the data directory exists and get its path
        file_prefix = ensure_data_directory_exists() + "/airodump"
        
        # Execute airodump-ng with the necessary arguments to write the scan results to files
        # The command outputs directly to the screen due to subprocess.run usage
        print("Starting airodump-ng... Press Ctrl+C to stop.")
        process = subprocess.Popen(['airodump-ng', '--write', file_prefix, '--output-format', 'csv', interface], text=True)
        
        # Wait for process to complete
        process.communicate()

    except KeyboardInterrupt:
        print("Airodump-ng scan stopped by user.")
        # Optional: Clean up or handle partially written data here

        # Send SIGTERM to the subprocess to ensure it's stopped
        process.send_signal(signal.SIGTERM)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    finally:
        print("Cleaning up...")

    print("Airodump-ng has finished scanning.")
    
    # After airodump-ng finishes or is interrupted, proceed with the rest of the function
    directory = ensure_data_directory_exists()
    csv_file = None
    for file in os.listdir(directory):
        if file.startswith("airodump") and file.endswith('.csv'):
            csv_file = directory + '/' + file
            break

    if csv_file is None:
        print("No CSV file generated by airodump-ng.")
        return
    
    # Process the CSV file to extract the data
    all_aps_filename = directory + '/access_points.txt'
    with open(all_aps_filename, 'w') as aps_file:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row, assuming it's there
            for row in csv_reader:
                if len(row) >= 14:  # Ensure the row has the expected number of elements
                    bssid = row[0].strip()
                    enc = row[5].strip()  # No need to check if empty
                    ssid = row[13].strip()
                    if bssid and ssid:  # Check for non-empty values of BSSID and SSID
                        aps_file.write(f"{bssid}, {enc}, {ssid}\n")
    print(f"Extraction complete. All access points have been saved to {all_aps_filename}")

def ask_for_scan(interface):
    response = input("Would you like to perform a scan with airodump-ng? (yes/no): ")
    if response.lower() == 'yes':
        run_airodump(interface)
    else:
        print("Exiting without scanning.")

def discovered_ap():
    file_path = "/mnt/data/access_points.txt"
    # Initialize the PrettyTable with the specified headers
    table = PrettyTable(["ESSID", "ENC", "BSSID"])

    try:
        # Open the file and read the contents using the csv.reader for parsing CSV formatted data
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                bssid, enc, essid = row  # Unpack the row directly into variables
                table.add_row([essid, enc, bssid])  # Add the data to the table

        print(table)  # Display the table
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def delete_accesspoints():
    file_path = "/mnt/data/access_points.txt"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Access Points Cleared Successfully.")
    else:
        print("/mnt/data/access_points.txt does not exist.")

def main():
    interface = 'wlan0'
    mon_interface = 'wlan0mon'

    # Check if wlan0mon is already in monitoring mode
    if is_monitor_mode_enabled(mon_interface):
        print(f"Monitoring mode is already enabled on: {mon_interface}")
        ask_for_scan(mon_interface)
    else:
        print("No network adapter is in monitoring mode.")
        user_input = input("Would you like to enable monitoring mode on wlan0? (yes/no): ")
        if user_input.lower() == 'yes':
            if enable_monitor_mode(interface):
                ask_for_scan(mon_interface)
        else:
            print("Exiting without enabling monitoring mode or scanning.")
