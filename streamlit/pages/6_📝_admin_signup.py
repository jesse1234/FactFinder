import streamlit as st
from utils.auth import signup_admin
from utils.auth_check import admin_check_unauth
import time

admin_check_unauth()

# Hide sidebar and customize header
st.set_page_config(
    page_title="Sign Up Page",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar and default menu
st.markdown("""
    <style>
         [data-testid="collapsedControl"] {display: none;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebarNav"] {display: none;}
            
        /* Custom header styling */
        .user-info {
            position: fixed;
            right: 20px;
            top: 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
            align-items: center;
            background-color: #1E1E1E;
            padding: 10px;
            border-radius: 5px;
        }
            
        .user-email {
            color: #FFFFFF;
            margin-right: 10px;
        }
            
        .logout-btn {
            background-color: #FF4B4B;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
        }
            
        .stApp > header {
            background-color: transparent;
        }
            
        .main-content {
            margin-top: 60px;  /* Add space for fixed header */
        }
                
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E;
            padding-top: 2rem;
        }
            
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            padding: 0 1rem;
        }
            
        /* Sidebar button styling */
        [data-testid="stSidebar"] button {
            background-color: transparent;
            border: 1px solid rgba(250, 250, 250, 0.1);
            transition: all 0.3s ease;
        }
            
        [data-testid="stSidebar"] button:hover {
            background-color: rgba(250, 250, 250, 0.1);
            border-color: rgba(250, 250, 250, 0.2);
        }
            
        /* Sidebar divider */
        [data-testid="stSidebar"] hr {
            margin: 2rem 0;
            border-color: rgba(250, 250, 250, 0.1);
        }
            
        /* Sidebar headings */
        [data-testid="stSidebar"] h3 {
            color: rgba(250, 250, 250, 0.8);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

def show_user_info():
    """Display user information in sidebar"""
    with st.sidebar:
        st.markdown("### Admin Navigation")

        if st.sidebar.button("🔐 Login", use_container_width=True, key='login_sidebar'):
            st.switch_page('pages/4_🔐_admin_login.py')

        if st.sidebar.button("📝 Sign Up", use_container_width=True, key='signup_sidebar'):
            st.switch_page('pages/6_📝_admin_signup.py')

def show_signup_page():

    show_user_info()

    st.title("Create Account")
    
    with st.form("signup_form"):
        new_email = st.text_input("Email")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not all([new_email, new_username, new_password, confirm_password]):
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, error = signup_admin(
                    new_email, 
                    new_username, 
                    new_password, 
                    confirm_password
                )
                if success:
                    st.success("Account created successfully!")
                    st.info("Redirecting to login page...")
                    time.sleep(2)  # Give time to see the success message
                    st.switch_page("pages/4_🔐_admin_login.py")
                else:
                    st.error(f"Sign up failed: {error}")

if not st.session_state.get('authenticated', False):
    show_signup_page()
else:
    st.success("You are already logged in!")
    if st.button("Go to Chat"):
        st.switch_page("pages/5_💬_admin_chat.py")