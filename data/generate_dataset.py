import pandas as pd
import random
import string
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.feature_extractor import extract_features, COMMON_PASSWORDS

def generate_weak_password():
    choice = random.randint(1, 4)
    if choice == 1:
        return random.choice(list(COMMON_PASSWORDS))
    elif choice == 2:
        return ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 7)))
    elif choice == 3:
        return ''.join(random.choices(string.digits, k=random.randint(4, 6)))
    else:
        char = random.choice(string.ascii_lowercase)
        return char * random.randint(4, 6)

def generate_medium_password():
    length = random.randint(8, 11)
    pool = string.ascii_letters + string.digits
    pw = list(''.join(random.choices(pool, k=length-2)))
    pw.append(random.choice(string.ascii_uppercase))
    pw.append(random.choice(string.digits))
    random.shuffle(pw)
    return ''.join(pw)

def generate_strong_password():
    length = random.randint(12, 16)
    pool = string.ascii_letters + string.digits + "!@#$%"
    pw = list(''.join(random.choices(pool, k=length-4)))
    pw.append(random.choice(string.ascii_uppercase))
    pw.append(random.choice(string.ascii_lowercase))
    pw.append(random.choice(string.digits))
    pw.append(random.choice("!@#$%"))
    random.shuffle(pw)
    return ''.join(pw)

def create_dataset(num_samples=3000):
    data = []
    
    for _ in range(num_samples // 3):
        # Weak = 0
        pw_weak = generate_weak_password()
        feats_weak = extract_features(pw_weak)
        feats_weak['label'] = 0
        data.append(feats_weak)
        
        # Medium = 1
        pw_med = generate_medium_password()
        feats_med = extract_features(pw_med)
        feats_med['label'] = 1
        data.append(feats_med)
        
        # Strong = 2
        pw_strong = generate_strong_password()
        feats_strong = extract_features(pw_strong)
        feats_strong['label'] = 2
        data.append(feats_strong)
        
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv("data/passwords_dataset.csv", index=False)
    print(f"Dataset generated with {len(df)} samples at 'data/passwords_dataset.csv'")

if __name__ == "__main__":
    create_dataset()
