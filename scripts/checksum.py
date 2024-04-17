import hashlib
import os

CHECKSUM_DIR = "/mnt/data/"

def calculate_md5_checksum(file_path):
    #Calculate ther MD5 Checksum of a file
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def store_checksum(file_path, checksum):
    #Store the checksum 
    checksum_file_path = os.path.join(CHECKSUM_DIR, os.path.basename(file_path) + ".checksum")
    with open(checksum_file_path, "w") as f:
        f.write(checksum)

def read_stored_checksum(file_path):
    #Read the stored checksum
    checksum_file_path = os.path.join(CHECKSUM_DIR, os.path.basename(file_path) + ".checksum")
    try:
        with open(checksum_file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def check_file_integrity(file_path):
    #Check the integrity of a file
    stored_checksum = read_stored_checksum(file_path)
    if stored_checksum is None:
        print("No stored checksum found. Calculating and storing checksum...")
        current_checksum = calculate_md5_checksum(file_path)
        store_checksum(file_path, current_checksum)
        print("Checksum:", current_checksum)
        return True
    
    current_checksum = calculate_md5_checksum(file_path)
    if current_checksum == stored_checksum:
        print("Checksum:", current_checksum)
        return True
    else:
        print("Checksum:", current_checksum)
        print("File has changed.")
        choice = input("Would you like to update the checksum? (y/n): ")
        if choice.lower() == 'y':
            print("Updating checksum...")
            store_checksum(file_path, current_checksum)
            print("Checksum:", current_checksum)
        return False

def main():
    while True:
        try:
            file_path = input("Enter the file path to check: ")
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            print("File path invalid. Please enter a valid file path.")
            continue
        
        if check_file_integrity(file_path):
            print("File integrity preserved.")
        else:
            print("File has changed!")

        choice = input("Would you like to check another file? (y/n): ")
        if choice.lower() != 'y':
            break
