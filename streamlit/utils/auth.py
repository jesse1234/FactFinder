import requests
from typing import Tuple
import streamlit as st

FLASK_URL = "http://localhost:5000"

def login_user(email: str, password: str) -> tuple:
    """Handle user login"""
    try:
        response = requests.post(
            f"{FLASK_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )
        if response.status_code == 200:
            # Store both the session cookie and authenticated state
            st.session_state.session = response.cookies.get('session')
            st.session_state.authenticated = True
            st.session_state.user_email = email  # Optional: store user info
            return True, ""
        return False, response.json().get("error", "")
    except Exception as e:
        return False, str(e)

def signup_user(email: str, username: str, password1: str, password2: str) -> tuple:
    """Handle user signup"""
    try:
        response = requests.post(
            f"{FLASK_URL}/sign-up",
            json={
                "email": email,
                "username": username,
                "password1": password1,
                "password2": password2
            }
        )
        if response.status_code == 201:
            # Automatically log in after successful signup
            return login_user(email, password1)
        return False, response.json().get("error", "")
    except Exception as e:
        return False, str(e)

def login_admin(email: str, password: str) -> tuple:
    """Handle admin login"""
    try:
        response = requests.post(
            f"{FLASK_URL}/admin/login",
            json={
                "email": email,
                "password": password
            }
        )
        if response.status_code == 200:
            # Store both the session cookie and authenticated state
            st.session_state.session = response.cookies.get('session')
            st.session_state.authenticated = True
            st.session_state.is_admin = True  # Add admin flag
            st.session_state.user_email = email  # Optional: store admin info
            return True, ""
        return False, response.json().get("error", "")
    except Exception as e:
        return False, str(e)

def signup_admin(email: str, username: str, password1: str, password2: str) -> tuple:
    """Handle admin signup"""
    try:
        response = requests.post(
            f"{FLASK_URL}/admin/sign-up",
            json={
                "email": email,
                "username": username,
                "password1": password1,
                "password2": password2
            }
        )
        if response.status_code == 201:
            # Automatically log in after successful signup
            return login_admin(email, password1)
        return False, response.json().get("error", "")
    except Exception as e:
        return False, str(e)

def logout_user():
    """Handle user logout"""
    try:
        cookies = {'session': st.session_state.get('session')}
        response = requests.post(f"{FLASK_URL}/logout", cookies=cookies)
        # Clear session state
        st.session_state.clear()
        return True, ""
    except Exception as e:
        return False, str(e)