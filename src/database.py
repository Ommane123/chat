import sqlite3
import bcrypt
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_app.db")

def get_connection():
    # Allow multithreading as Streamlit might execute concurrently
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create password resets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            email TEXT PRIMARY KEY,
            otp TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL
        )
    ''')
    
    # Create chat sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create chat messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# --- User Auth Functions ---

def create_user(username, email, password):
    conn = get_connection()
    c = conn.cursor()
    
    # Hash password using bcrypt
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    try:
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        conn.commit()
        user_id = c.lastrowid
        return {"id": user_id, "username": username, "email": email}
    except sqlite3.IntegrityError as e:
        # User or email might already exist
        return None
    finally:
        conn.close()

def authenticate_user(username_or_email, password):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?',
              (username_or_email, username_or_email))
    user = c.fetchone()
    conn.close()
    
    if user:
        user_id, username, email, stored_hash = user
        # Check password against hash
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return {"id": user_id, "username": username, "email": email}
    
    return None

def check_username_exists(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    res = c.fetchone()
    conn.close()
    return bool(res)

def check_email_exists(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    res = c.fetchone()
    conn.close()
    return bool(res)

def save_password_reset_otp(email, otp):
    from datetime import datetime, timedelta
    conn = get_connection()
    c = conn.cursor()
    expires = datetime.now() + timedelta(minutes=15)
    c.execute('INSERT OR REPLACE INTO password_resets (email, otp, expires_at) VALUES (?, ?, ?)', (email, otp, expires))
    conn.commit()
    conn.close()

def verify_password_reset_otp(email, otp):
    from datetime import datetime
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now()
    
    c.execute('SELECT otp, expires_at FROM password_resets WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    
    if row:
        stored_otp, expires_at_str = row
        try:
            if '.' in expires_at_str:
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S.%f')
            else:
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
                
            if stored_otp == otp and now <= expires_at:
                return True
        except Exception:
            return False
            
    return False

def update_password(email, password):
    conn = get_connection()
    c = conn.cursor()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    c.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))
    c.execute('DELETE FROM password_resets WHERE email = ?', (email,))
    conn.commit()
    conn.close()
    return True

def delete_user_account(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    
    c.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    if row:
        email = row[0]
        c.execute('DELETE FROM password_resets WHERE email = ?', (email,))
        
    c.execute('SELECT session_id FROM chat_sessions WHERE user_id = ?', (user_id,))
    sessions = c.fetchall()
    for (session_id,) in sessions:
        c.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    
    c.execute('DELETE FROM chat_sessions WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# --- History Functions ---

def create_chat_session(user_id, session_id):
    conn = get_connection()
    c = conn.cursor()
    
    # Check if exists (e.g. from handle_new_chat multiple clicks)
    c.execute('SELECT session_id FROM chat_sessions WHERE session_id = ?', (session_id,))
    if c.fetchone() is None:
        c.execute('INSERT INTO chat_sessions (session_id, user_id) VALUES (?, ?)', (session_id, user_id))
        conn.commit()
    conn.close()

def delete_chat_session(session_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON') # Enable cascading deletes if needed, though we delete messages explicitly below just in case
    c.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    c.execute('DELETE FROM chat_sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)', (session_id, role, content))
    conn.commit()
    conn.close()

def get_user_sessions(user_id):
    conn = get_connection()
    c = conn.cursor()
    
    # Get all session ids
    c.execute('SELECT session_id FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    sessions = [row[0] for row in c.fetchall()]
    
    conn.close()
    return sessions

def get_session_messages(session_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
    messages = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return messages

# Init DB when module is loaded
init_db()
