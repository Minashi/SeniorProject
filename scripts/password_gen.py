
import random
import string

def generate_password(length, num_special_chars=0, num_digits=0):
    if length < num_special_chars + num_digits:
        raise ValueError("Length should be greater than or equal to the sum of special characters and digits.")

    num_chars = length - num_special_chars - num_digits
    chars = string.ascii_letters * 2 
    characters = chars + string.digits + string.punctuation


    password = ''.join(random.choice(characters) for _ in range(num_special_chars))
    password += ''.join(random.choice(string.digits) for _ in range(num_digits))
    password += ''.join(random.choice(chars) for _ in range(num_chars))
    

    password_list = list(password)
    random.shuffle(password_list)
    password = ''.join(password_list)

    return password

if __name__ == "__main__":
    length = int(input("Enter the desired length of the password: "))
    num_special_chars = int(input("Enter the number of special characters you want: "))
    num_digits = int(input("Enter the number of digits you want: "))

    try:
        password = generate_password(length, num_special_chars, num_digits)
        print("Generated password:", password)
    except ValueError as e:
        print(e)
