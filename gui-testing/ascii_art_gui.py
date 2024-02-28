import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # For displaying errors

def load_ascii_art(file_path="ascii_art.txt"):
    """
    Load ASCII art from a specified file.

    Parameters:
    - file_path: The path to the file containing ASCII art. Defaults to "ascii_art.txt".

    Returns:
    A string containing the ASCII art or an error message if the file cannot be found.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "ASCII Art File Not Found."

def display_ascii_art_gui(parent_root=None, file_path="ascii_art.txt"):
    """
    Display the ASCII art in a new GUI window.

    Parameters:
    - parent_root: The parent Tkinter root window. If None, a new root will be created.
    - file_path: The path to the ASCII art file. Defaults to "ascii_art.txt".
    """
    ascii_art = load_ascii_art(file_path)
    
    # If a parent root window is not provided, create a new Tkinter root
    if parent_root is None:
        parent_root = tk.Tk()
        parent_root.withdraw()  # Optionally hide the parent root if it's newly created

    art_window = tk.Toplevel(parent_root)
   
