import streamlit as st
import re
from src.database import create_user, authenticate_user, check_username_exists, check_email_exists

def is_valid_password(password):
    return len(password) >= 8

def login_form():
    st.subheader("Welcome Back")
    username_or_email = st.text_input("Username or Email", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", use_container_width=True, type="primary"):
        if not username_or_email or not password:
            st.error("Please fill in all fields.")
        else:
            user = authenticate_user(username_or_email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username/email or password.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Forgot Password?", use_container_width=True, type="secondary"):
        st.session_state.auth_mode = "Forgot Password"
        st.rerun()

def signup_form():
    st.subheader("Create an Account")
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    
    if st.button("Sign Up", use_container_width=True, type="primary"):
        if not email or not username or not password or not confirm_password:
            st.error("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return
            
        if not is_valid_password(password):
            st.error("Password must be at least 8 characters long.")
            return
            
        if check_email_exists(email):
            st.error("Email is already registered.")
            return
            
        if check_username_exists(username):
            st.error("Username is already taken.")
            return
            
        user = create_user(username, email, password)
        if user:
            st.success("Account created successfully! You are now logged in.")
            st.session_state.user = user
            st.rerun()
        else:
            st.error("An error occurred while creating your account. Please try again.")

def forgot_password_form():
    from src.database import check_email_exists, save_password_reset_otp, verify_password_reset_otp, update_password
    from src.email_utils import generate_otp, send_otp_email

    st.subheader("Recover Password")
    
    if "fp_step" not in st.session_state:
        st.session_state.fp_step = "email"
        
    if st.session_state.fp_step == "email":
        email = st.text_input("Enter your registered email address")
        if st.button("Send OTP", use_container_width=True, type="primary"):
            if not email:
                st.error("Please enter your email.")
            elif not check_email_exists(email):
                st.error("Email not found in our records.")
            else:
                otp = generate_otp()
                save_password_reset_otp(email, otp)
                if send_otp_email(email, otp):
                    st.session_state.fp_email = email
                    st.session_state.fp_step = "otp"
                    st.success("OTP sent to your email!")
                    st.rerun()
                else:
                    st.error("Failed to send OTP email. Please check configuration.")
                    
    elif st.session_state.fp_step == "otp":
        st.info(f"OTP sent to {st.session_state.fp_email}")
        otp_input = st.text_input("Enter 6-digit OTP")
        if st.button("Verify OTP", use_container_width=True, type="primary"):
            if not otp_input:
                st.error("Please enter the OTP.")
            elif verify_password_reset_otp(st.session_state.fp_email, otp_input):
                st.session_state.fp_step = "password"
                st.success("OTP Verified!")
                st.rerun()
            else:
                st.error("Invalid or expired OTP. Please try again.")
                
    elif st.session_state.fp_step == "password":
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Reset Password", use_container_width=True, type="primary"):
            if not new_password or not confirm_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not is_valid_password(new_password):
                st.error("Password must be at least 8 characters long.")
            else:
                update_password(st.session_state.fp_email, new_password)
                st.success("Password reset successfully! You can now log in.")
                st.session_state.auth_mode = "Login"
                del st.session_state.fp_step
                del st.session_state.fp_email
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to Login", use_container_width=True):
        st.session_state.auth_mode = "Login"
        if "fp_step" in st.session_state:
            del st.session_state.fp_step
        if "fp_email" in st.session_state:
            del st.session_state.fp_email
        st.rerun()

def show_auth_screen():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🤖 AI-Powered Chatbot")
        st.markdown("Please log in or sign up to continue. Your chat history will be securely saved.")
        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "Login"
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", use_container_width=True, type="primary" if st.session_state.auth_mode == "Login" else "secondary"):
                st.session_state.auth_mode = "Login"
                st.rerun()
        with col2:
            if st.button("📝 Sign Up", use_container_width=True, type="primary" if st.session_state.auth_mode == "Sign Up" else "secondary"):
                st.session_state.auth_mode = "Sign Up"
                st.rerun()
                
        with st.container(border=True):
            if st.session_state.auth_mode == "Login":
                login_form()
            elif st.session_state.auth_mode == "Sign Up":
                signup_form()
            elif st.session_state.auth_mode == "Forgot Password":
                forgot_password_form()
