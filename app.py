import streamlit as st
import sqlite3
from hashlib import sha256  # For password hashing

# ===== Database Setup =====
conn = sqlite3.connect('video_db.sqlite3')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    duration TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL
)''')
conn.commit()

# ===== Password Security =====
def create_user(username, password):
    """Add new user with hashed password"""
    password_hash = sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
    conn.commit()

def verify_user(username, password):
    """Check if login is valid"""
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0] == sha256(password.encode()).hexdigest()
    return False

# ===== Video Operations =====
def list_videos():
    cursor.execute("SELECT * FROM videos ORDER BY upload_date DESC")
    return cursor.fetchall()

def add_video(name, duration):
    cursor.execute("INSERT INTO videos (name, duration) VALUES (?, ?)", 
                  (name, duration))
    conn.commit()

# ===== Streamlit UI =====
def login_page():
    """Login/Signup Interface"""
    st.title("?? Video Manager Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        if st.button("Create Account"):
            create_user(new_user, new_pass)
            st.success("Account created! Please login")

def main_app():
    """Main Application After Login"""
    st.title(f"?? Video Manager (Welcome {st.session_state.user})")
    
    with st.sidebar:
        st.header("Actions")
        action = st.radio("Select Operation", 
                         ["View Videos", "Add Video", "Delete Videos"])
    
    if action == "View Videos":
        st.subheader("Your Video Library")
        videos = list_videos()
        if videos:
            for vid in videos:
                with st.expander(f"?? {vid[1]}"):
                    st.write(f"?? Duration: {vid[2]}")
                    st.write(f"?? Uploaded: {vid[3]}")
                    if st.button(f"Delete {vid[1]}", key=f"del_{vid[0]}"):
                        cursor.execute("DELETE FROM videos WHERE id=?", (vid[0],))
                        conn.commit()
                        st.rerun()
        else:
            st.info("No videos found. Add one below!")
    
    elif action == "Add Video":
        st.subheader("Upload New Video")
        with st.form("add_form"):
            name = st.text_input("Video Title")
            duration = st.text_input("Duration (e.g., 2:30)")
            if st.form_submit_button("Upload"):
                add_video(name, duration)
                st.success("Video added successfully!")
                st.rerun()

# ===== App Flow Control =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_page()

# Close connection when done
conn.close()