import subprocess, netifaces

def get_network_interfaces():
    """ Retrieve available network interfaces and their associated IP addresses. """
    interfaces = netifaces.interfaces()
    addresses = {}
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        ipv4 = addrs.get(netifaces.AF_INET)
        if ipv4:
            addresses[interface] = ipv4[0]['addr']
    return addresses

def select_network_interface():
    """ Display a list of network interfaces for the user to select from. """
    addresses = get_network_interfaces()
    if not addresses:
        print("No network interfaces with IPv4 found.")
        return None, None
    print("Available network interfaces:")
    for idx, (interface, ip) in enumerate(addresses.items(), start=1):
        print(f"{idx}: {interface} ({ip})")
    selection = int(input("Select an interface to scan: "))
    interface = list(addresses.keys())[selection - 1]
    ip_base = addresses[interface].rsplit('.', 1)[0] + '.0/24'
    return interface, ip_base

def basic_lan_scan():
    interface, target = select_network_interface()
    if not interface:
        return
    try:
        print(f"Scanning {target} on interface {interface}...")
        subprocess.run(['nmap', '-v', '-e', interface, target], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the scan: {e}")
    except KeyboardInterrupt:
        print("Scan canceled by user. Returning to main application.")

def scan_for_vulnerabilities():
    interface, target = select_network_interface()
    if not interface:
        return
    print(f"Scanning {target} on interface {interface} for common vulnerabilities...")
    try:
        subprocess.run(['nmap', '-e', interface, '-sV', '-v', '--script=vuln', target], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the vulnerability scan: {e}")
    except KeyboardInterrupt:
        print("Vulnerability scan canceled by user. Returning to main application.")

def list_nmap_script_options():
    # List of commonly used Nmap scripts and their descriptions
    nmap_scripts = [
        {"script": "vuln", "description": "General vulnerability scanning"},
        {"script": "smb-vuln-ms17-010", "description": "Check for EternalBlue vulnerability (MS17-010)"},
        {"script": "http-heartbleed", "description": "Test for Heartbleed vulnerability in SSL/TLS"},
        {"script": "smb-vuln-cve-2017-5689",
         "description": "Check for Intel AMT security vulnerability (CVE-2017-5689)"},
        {"script": "rdp-vuln-ms12-020", "description": "Check for vulnerabilities in Microsoft RDP (CVE-2019-0708)"},
        {"script": "smb-vuln-cve-2020-0796",
         "description": "Check for SMBGhost vulnerability in SMBv3 (CVE-2020-0796)"},
        {"script": "ssh-vuln-cve-2018-10933", "description": "Check for vulnerability in libssh (CVE-2018-10933)"},
        {"script": "http-title", "description": "Get the title of the web server's default page"},
        {"script": "ssl-enum-ciphers", "description": "Enumerate SSL/TLS ciphers and protocols"},
        {"script": "smb-os-discovery", "description": "Discover OS, computer name, and more over SMB"},
        {"script": "dns-zone-transfer", "description": "Attempt a DNS zone transfer"},
        {"script": "broadcast-dhcp-discover", "description": "Discover DHCP servers in the local network"},
        {"script": "mysql-vuln-cve2012-2122",
         "description": "Check for MySQL auth bypass vulnerability (CVE-2012-2122)"},
        {"script": "ssh2-enum-algos", "description": "Enumerate SSH protocol 2 algorithms supported by the server"},
    ]

    print("Available Nmap Script Options:")
    for i, script in enumerate(nmap_scripts, start=1):
        print(f"{i}. {script['script']} - {script['description']}")

    return nmap_scripts

def custom_nmap_script_scan():
    nmap_scripts = list_nmap_script_options()  # Display script options and get the list

    script_choice = input("Select a script by number or enter script name directly: ")
    try:
        script_choice = int(script_choice) - 1
        script = nmap_scripts[script_choice]['script']
    except ValueError:
        script = script_choice

    # Display information about the vulnerability associated with the selected script
    if script in vulnerabilities_info:
        vuln_info = vulnerabilities_info[script]
        print(f"\nSelected Script: {script}")
        print(f"Vulnerability Name: {vuln_info['name']}")
        print(f"Description: {vuln_info['description']}")
        print(f"Remediation: {vuln_info['remediation']}\n")
    else:
        print(f"\nSelected Script: {script}")
        print("No specific vulnerability information available for this script.\n")

    # Confirm with the user to proceed with the scan
    proceed = input("Proceed with the scan? (yes/no): ").lower()
    if proceed != 'yes':
        print("Scan cancelled.")
        return

    interface, target = select_network_interface()
    if not interface:
        return
    print(f"\nRunning Nmap script ({script}) on {target}...")
    try:
        result = subprocess.run(['nmap', '-v', '-e', interface, '--script', script, target], 
                                capture_output=True, text=True, check=True)
        print("Scan complete.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the custom script scan: {e}")
    except KeyboardInterrupt:
        print("Custom script scan canceled by user. Exiting gracefully.")

vulnerabilities_info = {
    "smb-vuln-ms17-010": {
        "name": "EternalBlue MS17-010",
        "description": "Allows remote code execution due to improper handling of SMB packets.",
        "remediation": "Apply the MS17-010 security update."
    },
    "http-heartbleed": {
        "name": "Heartbleed",
        "description": "A serious vulnerability in the OpenSSL cryptographic software library, allowing attackers to read the memory of servers running vulnerable versions of OpenSSL.",
        "remediation": "Update OpenSSL to version 1.0.1g or later, or recompile OpenSSL without the heartbeat option."
    },
    "smb-vuln-cve-2017-5689": {
        "name": "Intel AMT CVE-2017-5689",
        "description": "A vulnerability in some Intel Active Management Technology, Intel Small Business Technology, and Intel Standard Manageability allows unprivileged network attacker to gain system privileges.",
        "remediation": "Apply Intel firmware updates and check vendor advisories for specific patching instructions."
    },
    "rdp-vuln-ms12-020": {
        "name": "MS12-020 RDP Vulnerability",
        "description": "A pair of vulnerabilities in Microsoft's implementation of the Remote Desktop Protocol (RDP) could allow remote code execution.",
        "remediation": "Install the updates provided by Microsoft in the MS12-020 bulletin."
    },
    "smb-vuln-cve-2020-0796": {
        "name": "SMBGhost",
        "description": "A vulnerability in the Microsoft Server Message Block 3.1.1 (SMBv3) protocol could allow for remote code execution.",
        "remediation": "Apply the update provided by Microsoft addressing this vulnerability (KB4551762)."
    },
    "ssh-vuln-cve-2018-10933": {
        "name": "libssh Authentication Bypass",
        "description": "A vulnerability in libssh could allow an attacker to successfully bypass authentication procedures without any valid credentials.",
        "remediation": "Update the libssh library to version 0.7.6 or later."
    },
    "mysql-vuln-cve2012-2122": {
        "name": "MySQL Auth Bypass CVE-2012-2122",
        "description": "A vulnerability in MySQL and MariaDB that allows an attacker to authenticate as any user if they attempt enough times, due to a flaw in the password checking algorithm.",
        "remediation": "Update MySQL and MariaDB installations to a version that has fixed this vulnerability. For MySQL, versions 5.1.63, 5.5.25, 5.6.7 and later include the fix."
    },
    # The following entries are placeholders. You should fill them in based on the script's purpose and known vulnerabilities it detects.
    "http-title": {
        "name": "Web Server Title Disclosure",
        "description": "Discloses the title of the web server's default page, which could provide sensitive information.",
        "remediation": "Review the web server configuration to limit information disclosure in titles and headers."
    },
    "ssl-enum-ciphers": {
        "name": "Weak SSL/TLS Ciphers Enumeration",
        "description": "Enumerates supported SSL/TLS ciphers and protocols, identifying weak cryptographic standards.",
        "remediation": "Configure the server to use strong ciphers and disable weak ones. Prefer TLS 1.2 or higher."
    },
    "smb-os-discovery": {
        "name": "SMB OS and NetBIOS Information Discovery",
        "description": "Discloses information about the operating system and NetBIOS over SMB, potentially revealing sensitive details.",
        "remediation": "Limit SMB exposure to trusted networks and configure firewalls to block unauthorized SMB traffic."
    },
    "dns-zone-transfer": {
        "name": "DNS Zone Transfer",
        "description": "Attempts to perform a DNS zone transfer which could disclose all the DNS records for a domain.",
        "remediation": "Restrict zone transfers to authorized DNS servers and configure DNS servers securely."
    },
    "broadcast-dhcp-discover": {
        "name": "DHCP Server Discovery",
        "description": "Discovers DHCP servers on the local network, which could reveal unauthorized DHCP services.",
        "remediation": "Ensure only authorized DHCP servers are operational and monitor for rogue DHCP server presence."
    },
    "ssh2-enum-algos": {
        "name": "SSH Algorithms Enumeration",
        "description": "Enumerates supported SSH algorithms, potentially identifying weak algorithms allowed by the server.",
        "remediation": "Configure SSH servers to use strong encryption algorithms and disable weak ones."
    },
}
