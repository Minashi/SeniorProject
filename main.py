import time
import sys
import os

def check_root_user():
    if os.geteuid() != 0:
        print("This script must be run as root. Exiting.")
        sys.exit(1)

def loading_prompt(message="", art=None):
    if art:
        print(art)
    print(message)
    for _ in range(3):  # Simple loading animation
        print(".", end="", flush=True)
        time.sleep(1)
    print("\n")

# Start up ASCII Art
ascii_art = """
   ___  
  /   \\\\
 /     \\\\
/_______\\\\
\_______/
"""

# MENU OPTIONS
def menu_option_1():
    print("Access Point Enumeration Here")

def menu_option_2():
    print("List out discovered Access Points")

def menu_option_3():
    print("Crack WEP Access Points")
# More functions can be added here as needed.

# PIVOT MENU OPTIONS
def submenu_option_1():
    print("List Cracked Passwords")

def submenu_option_2():
    print("Connect To Accesspoint using specified access point")
    
def submenu_option_3():
    print("Enumerate LAN")
# More functions can be added here as needed.

# NAVIGATION
def menu_to_submenu():
    print("Entering Main menu...")
    display_submenu()

def exit_menu():
    print("Exiting menu...")

def display_menu():
    # Define menu options here. Add new options by appending to this list.
    menu_options = [
        {"label": "Access Point Enumeration", "function": menu_option_1},
        {"label": "List Discovered Access Points", "function": menu_option_2},
        {"label": "Crack WEP", "function": menu_option_3},
        {"label": "Pivot", "function": menu_to_submenu},
        # Add new options in this format.
        {"label": "Exit", "function": exit_menu},
    ]
    
    while True:
        print("\nMenu:")
        for i, option in enumerate(menu_options, start=1):
            print(f"{i}. {option['label']}")
        
        try:
            choice = int(input("Select an option: "))
            if 1 <= choice <= len(menu_options):
                menu_options[choice - 1]["function"]()
                if menu_options[choice - 1]["label"] == "Exit":
                    break
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting due to Ctrl+C")
            break

def display_submenu():
    submenu_options = [
        {"label": "List Cracked Passwords", "function": submenu_option_1},
        {"label": "Pivot To Access Point", "function": submenu_option_2},
        {"label": "Enumerate LAN", "function": submenu_option_3},
        {"label": "Exit Pivot Menu", "function": exit_menu},
    ]
    
    while True:
        print("\nPivot:")
        for i, option in enumerate(submenu_options, start=1):
            print(f"{i}. {option['label']}")
        
        choice = int(input("Select an option: "))
        if 1 <= choice <= len(submenu_options):
            submenu_options[choice - 1]["function"]()
            if submenu_options[choice - 1]["label"] == "Exit Pivot Menu":
                break
        else:
            print("Invalid option, please try again.")

# Check if the user is root before proceeding
check_root_user()

# Initiate loading menu
loading_prompt("Initializing menu", ascii_art)
display_menu()
