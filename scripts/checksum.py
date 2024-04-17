import hashlib

def calculate_md5_checksum(file_path):
    
    #Calculate the MD5 checksum of a file. 
    #file_path (str): The path to the file.   str: The MD5 checksum of the file.

    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def store_checksum(file_path, checksum):
    #store the checksum
    with open(file_path + ".checksum", "w") as f:
        f.write(checksum)

def read_stored_checksum(file_path):
    #read stored checksum
    try:
        with open(file_path + ".checksum", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def check_file_integrity(file_path):
    stored_checksum = read_stored_checksum(file_path)
    if stored_checksum is None:
        print("No stored checksum found. Calculating and storing checksum...")
        current_checksum = calculate_md5_checksum(file_path)
        store_checksum(file_path, current_checksum)
        print("Checksum:", current_checksum)  # Print the checksum
        return True
    
    current_checksum = calculate_md5_checksum(file_path)
    if current_checksum == stored_checksum:
        print("Checksum:", current_checksum)  # Print the checksum
        return True
    else:
        print("Checksum:", current_checksum)  # Print the checksum
        print("File has changed.")
        choice = input("Would you like to calculate and update the checksum? (y/n): ")
        if choice.lower() == 'y':
            print("Updating checksum...")
            store_checksum(file_path, current_checksum)
            print("Checksum:", current_checksum)  # Print the checksum
        return False

def main():
    while True:
        try:
            # User input for the file path
            file_path = input("Enter the file path to check: ")
            # Check if the file exists
            with open(file_path, 'r'):
                pass
        #If an invalid file path is entered, prompt for a different path
        except FileNotFoundError: 
            print("File path invalid. Please enter a valid file path.")
            continue
        
        # Check if the file has changed since the last checksum calculation
        if check_file_integrity(file_path):
            print("File integrity preserved.")
        else:
            print("File has changed!")

        # Ask if the user wants to check another file
        choice = input("Would you like to check another file? (y/n): ")
        if choice.lower() != 'y':
            break
