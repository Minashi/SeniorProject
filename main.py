def menu_option_1():
    print("You selected option 1.")

def menu_option_2():
    print("You selected option 2.")

# More functions can be added here as needed.

def exit_menu():
    print("Exiting menu...")

# Define menu options here.
menu_options = [
    {"label": "Option 1", "function": menu_option_1},
    {"label": "Option 2", "function": menu_option_2},
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

# Run the menu
display_menu()
