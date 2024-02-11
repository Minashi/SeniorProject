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

def menu_option_1():
    print("Access Point Enumeration Here")

def menu_option_2():
    print("List out discovered Access Points")

def menu_option_3():
    print("Crack WEP Access Points")

# More functions can be added here as needed.

def exit_menu():
    print("Exiting menu...")

# Define menu options here. Add new options by appending to this list.
menu_options = [
    {"label": "Option 1", "function": menu_option_1},
    {"label": "Option 2", "function": menu_option_2},
    {"label": "Option 3", "function": menu_option_3},
    # Add new options in this format.
    {"label": "Exit", "function": exit_menu},
]

def display_menu():
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

# Check if the user is root before proceeding
check_root_user()

# Initiate loading menu
loading_prompt("Initializing menu", ascii_art)
display_menu()
