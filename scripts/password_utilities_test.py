import random
import string

def generate_password(length, num_special_chars=0, num_digits=0):
    if length < num_special_chars + num_digits:
        raise ValueError("Length should be greater than or equal to the sum of special characters and digits.")

    # Adjusting the calculation for the number of characters
    num_chars = length - num_special_chars - num_digits

    # Separating character types
    chars = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    # Ensuring each type of character is included as requested
    password = ''.join(random.choice(special_chars) for _ in range(num_special_chars))
    password += ''.join(random.choice(digits) for _ in range(num_digits))
    password += ''.join(random.choice(chars) for _ in range(num_chars))

    # Randomizing the order of characters in the password
    password_list = list(password)
    random.shuffle(password_list)
    password = ''.join(password_list)

    return password

def test_password_strength(password):
    length = len(password)
    has_lowercase = any(char.islower() for char in password)
    has_uppercase = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in '-=[]{}|;:,.<>?/~!@#$%^&*()_+' for char in password)

    if length < 6:
        return 'very weak'
    elif length < 8:
        return 'weak'
    elif length < 12:
        if has_lowercase and has_uppercase and has_digit or has_special: 
            return 'normal'
        else:
            return 'weak'
    elif length < 15:
        if has_lowercase and has_uppercase and has_digit and has_special:
            return 'strong'
        elif (has_lowercase or has_uppercase) and (has_digit or has_special):
            return 'normal'
        else:
            return 'weak'
    elif length >= 16:
        if has_lowercase and has_uppercase and has_digit and has_special:
            return 'very strong'
        elif (has_lowercase and has_uppercase) and (has_digit or has_special):
            return 'strong'
        elif (has_lowercase or has_uppercase) and (has_digit or has_special):
            return 'normal'
        else:
            return 'weak'
    else:
        return 'error'

def generate_password_interface():
    print("\nPassword Generator")
    length = int(input("Enter the desired length of the password: "))
    num_special_chars = int(input("Enter the number of special characters you want: "))
    num_digits = int(input("Enter the number of digits you want: "))

    try:
        password = generate_password(length, num_special_chars, num_digits)
        print("Generated password:", password)
    except ValueError as e:
        print(e)

def test_password_strength_interface():
    print("\nPassword Strength Tester")
    password = input("Enter the password to test its strength: ")
    strength = test_password_strength(password)
    print(f"The password strength is: {strength}")
