import random
import string

def generate_password(length=12):
    """Generate a random password with letters, digits, and punctuation."""
    if length < 4:
        raise ValueError("Password length should be at least 4 characters.")
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

# Example usage:
print(generate_password(23))