import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

def init_db():
    """Initializes the database structure if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    
    # Create keystrokes table (temporarily storing simple lists of metrics as JSON)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keystrokes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        features JSON NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password):
    """Registers a new user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, generate_password_hash(password)))
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def authenticate_user(username, password):
    """Checks if username and password match."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return True, user[0]
    return False, None

def save_keystroke_profile(user_id, features_dict):
    """Saves a single instance of typing dynamics features."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO keystrokes (user_id, features) VALUES (?, ?)", 
                   (user_id, json.dumps(features_dict)))
    conn.commit()
    conn.close()

def get_keystroke_profiles(user_id):
    """Retrieves all historical keystroke profiles for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT features FROM keystrokes WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [json.loads(row[0]) for row in rows]
