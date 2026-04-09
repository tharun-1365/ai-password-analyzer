import string
import math
import re

COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "12345", "1234", "111111", 
    "1234567", "dragon", "123123", "baseball", "monkey", "letmein", "football", 
    "shadow", "mustang", "superman", "hello", "12345678", "abc123", "asdfgh", "admin"
}

def calculate_entropy(password):
    if not password:
        return 0
    entropy = 0
    pool_size = 0
    if any(c.islower() for c in password): pool_size += 26
    if any(c.isupper() for c in password): pool_size += 26
    if any(c.isdigit() for c in password): pool_size += 10
    if any(c in string.punctuation for c in password): pool_size += 32
    
    if pool_size == 0:
        return 0
        
    return len(password) * math.log2(pool_size)

def has_sequential_chars(password):
    if len(password) < 3:
        return 0
    for i in range(len(password) - 2):
        if ord(password[i]) + 1 == ord(password[i+1]) and ord(password[i+1]) + 1 == ord(password[i+2]):
            return 1
        if ord(password[i]) - 1 == ord(password[i+1]) and ord(password[i+1]) - 1 == ord(password[i+2]):
            return 1
    # Check common keyboard sequences
    lower_pw = password.lower()
    qwerty_seq = ["qwerty", "asdfgh", "zxcvbn", "qwert"]
    for seq in qwerty_seq:
        if seq in lower_pw:
            return 1
    return 0

def has_repeated_chars(password):
    if re.search(r'(.)\1\1', password): # 3 the same in a row
        return 1
    return 0

def is_common_password(password):
    return 1 if password.lower() in COMMON_PASSWORDS else 0

def extract_features(password):
    return {
        "length": len(password),
        "num_upper": sum(1 for c in password if c.isupper()),
        "num_lower": sum(1 for c in password if c.islower()),
        "num_digits": sum(1 for c in password if c.isdigit()),
        "num_special": sum(1 for c in password if c in string.punctuation),
        "repeated": has_repeated_chars(password),
        "sequential": has_sequential_chars(password),
        "common": is_common_password(password),
        "entropy": calculate_entropy(password)
    }

def get_feedback(password):
    feedback = []
    if len(password) < 8:
        feedback.append("Password is too short. Use at least 8 characters.")
    if sum(1 for c in password if c.isupper()) == 0:
        feedback.append("Add uppercase letters.")
    if sum(1 for c in password if c.islower()) == 0:
        feedback.append("Add lowercase letters.")
    if sum(1 for c in password if c.isdigit()) == 0:
        feedback.append("Include digits.")
    if sum(1 for c in password if c in string.punctuation) == 0:
        feedback.append("Add special characters (e.g. !@#$).")
    if is_common_password(password):
        feedback.append("This is a very common password, please avoid using it.")
    if has_sequential_chars(password):
        feedback.append("Avoid sequential characters like '123' or 'abc'.")
    if has_repeated_chars(password):
        feedback.append("Avoid repeating exactly the same character (e.g. 'aaa').")
        
    if len(feedback) == 0:
        feedback.append("Looks good! No obvious rules violated.")
        
    return feedback
