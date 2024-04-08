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
    elif length < 10:
        if has_lowercase and has_uppercase and (has_digit or has_special):
            return 'normal'
        else:
            return 'weak'
    elif length < 12:
        if (has_lowercase and has_uppercase) or (has_digit and has_special):
            return 'strong'
        else:
            return 'normal'
    elif length >= 18:
        if has_lowercase and has_uppercase and has_digit and has_special:
            return 'very strong'
        elif (has_lowercase and has_uppercase) or (has_digit and has_special):
            return 'strong'
        else:
            return 'normal'
    else:
        return 'strong'

if __name__ == "__main__":
    password = input("Enter your password: ")
    strength = test_password_strength(password)
    print("Password strength:", strength)
