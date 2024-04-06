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

def list_credentials():
    # list username, password (if found), and hash
    pass

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
