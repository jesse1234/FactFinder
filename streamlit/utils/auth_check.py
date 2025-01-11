import streamlit as st
import requests

FLASK_URL = "http://localhost:5000"

def verify_session():
    """Verify if the current session is valid"""
    if 'session' not in st.session_state:
        return False
    
    try:
        cookies = {'session': st.session_state.session}
        response = requests.get(
            f"{FLASK_URL}/verify-session",  # You'll need to create this endpoint
            cookies=cookies
        )
        return response.status_code == 200
    except:
        return False

def check_auth():
    """Check authentication and redirect if needed"""
    if not st.session_state.get('authenticated', False):
        st.switch_page('pages/1_🔐_login.py')
        st.stop()
    
    # Verify session is still valid
    if not verify_session():
        st.session_state.clear()
        st.switch_page('pages/1_🔐_login.py')
        st.stop()

def check_unauth():
    """Check if user is authenticated, redirect to chat if they are"""
    if st.session_state.get('authenticated', False) and verify_session():
        st.switch_page('pages/3_💬_Chat.py')
        st.stop()

def admin_check_auth():
    """Check authentication and redirect if needed"""
    if not (st.session_state.get('authenticated', False) and 
            st.session_state.get('is_admin', False)):
        st.switch_page('pages/4_🔐_admin_login.py')
        st.stop()
    
    # Verify session is still valid
    if not verify_session():
        st.session_state.clear()
        st.switch_page('pages/4_🔐_admin_login.py')
        st.stop()

def admin_check_unauth():
    """Check if admin is authenticated, redirect to admin chat if they are"""
    if (st.session_state.get('authenticated', False) and 
        st.session_state.get('is_admin', False) and 
        verify_session()):
        st.switch_page('pages/5_💬_admin_chat.py')
        st.stop()