import streamlit as st
from streamlit.components.v1 import html
import re
import hashlib
import sqlite3
from PIL import Image
import time
st.set_page_config(
    page_title="Account Management",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)
def inject_custom_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stTextInput>div>div>input, .stPassword>div>div>input {
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ced4da;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            padding: 10px;
            background-color: #4a90e2;
            color: white;
            border: none;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #357abd;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .subtitle {
            font-size: 1rem;
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 2rem;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .success-message {
            color: #27ae60;
            text-align: center;
            margin-top: 1rem;
        }
        .error-message {
            color: #e74c3c;
            text-align: center;
            margin-top: 1rem;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #95a5a6;
            font-size: 0.8rem;
        }
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin: 0 auto 1rem auto;
            display: block;
            object-fit: cover;
            border: 3px solid #4a90e2;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()
def init_db():
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def validate_username(username):
    if len(username) < 4:
        return "Username must be at least 4 characters long"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores"
    return None

def validate_email(email):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return "Please enter a valid email address"
    return None

def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"
    return None

def validate_phone(phone):
    if phone and not re.match(r"^\+?[0-9\s\-]+$", phone):
        return "Please enter a valid phone number"
    return None
def register_user(username, email, password, phone):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    if c.fetchone():
        conn.close()
        return False, "Username or email already exists"
    
    hashed_pw = hash_password(password)
    c.execute(
        "INSERT INTO users (username, email, password, phone) VALUES (?, ?, ?, ?)",
        (username, email, hashed_pw, phone))
    conn.commit()
    conn.close()
    return True, "Registration successful"

def login_user(username, password):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    hashed_pw = hash_password(password)
    
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    
    if user:
        return True, user
    return False, "Invalid username or password"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
def show_login_form():
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h1 class="title">Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Sign in to access your account</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Remember me")
            
            submitted = st.form_submit_button("Login")
            if submitted:
                username_error = validate_username(username)
                password_error = validate_password(password)
                
                if username_error:
                    st.error(username_error)
                elif password_error:
                    st.error(password_error)
                else:
                    success, result = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_info = {
                            "id": result[0],
                            "username": result[1],
                            "email": result[2],
                            "phone": result[4]
                        }
                        st.success("Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(result)
        
        st.markdown('<p style="text-align: center; margin-top: 1rem;">Don\'t have an account? <a href="#register">Register here</a></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_register_form():
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h1 class="title">Create Account</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Join us today and get started</p>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            phone = st.text_input("Phone Number (optional)", placeholder="+1234567890")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            submitted = st.form_submit_button("Register")
            if submitted:
                errors = []
                
                username_error = validate_username(username)
                email_error = validate_email(email)
                password_error = validate_password(password)
                phone_error = validate_phone(phone)
                
                if username_error:
                    errors.append(username_error)
                if email_error:
                    errors.append(email_error)
                if password_error:
                    errors.append(password_error)
                if phone_error:
                    errors.append(phone_error)
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    success, message = register_user(username, email, password, phone)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.session_state.show_login = True
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown('<p style="text-align: center; margin-top: 1rem;">Already have an account? <a href="#login">Login here</a></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<h1 class="title">Welcome, {st.session_state.username}!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">You are now logged in to your account</p>', unsafe_allow_html=True)
        
        # User avatar placeholder
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<img src="https://ui-avatars.com/api/?name=' + st.session_state.username + '&background=4a90e2&color=fff&size=200" class="avatar">', unsafe_allow_html=True)
        
        
        st.markdown("### Account Information")
        user_info = st.session_state.user_info
        st.write(f"**Username:** {user_info['username']}")
        st.write(f"**Email:** {user_info['email']}")
        if user_info['phone']:
            st.write(f"**Phone:** {user_info['phone']}")
        
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.success("You have been logged out successfully!")
            time.sleep(1)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    
    if st.session_state.logged_in:
        show_dashboard()
    else:
        if st.session_state.show_login:
            show_login_form()
            if st.button("Create New Account"):
                st.session_state.show_login = False
                st.rerun()
        else:
            show_register_form()
            if st.button("Back to Login"):
                st.session_state.show_login = True
                st.rerun()
    
    st.markdown('<p class="footer">© 2025 Account Management. All rights reserved.</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
