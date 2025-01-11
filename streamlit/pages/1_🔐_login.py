import streamlit as st
from utils.auth import login_user
from utils.auth_check import check_unauth
import time

check_unauth()

# Hide sidebar and customize header
st.set_page_config(
    page_title="Login Page",
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
        st.markdown("### Navigation")

        if st.sidebar.button("🔐 Login", use_container_width=True, key='login_sidebar'):
            st.switch_page('pages/1_🔐_login.py')

        if st.sidebar.button("📝 Sign Up", use_container_width=True, key='signup_sidebar'):
            st.switch_page('pages/2_📝_signup.py')

        for _ in range(20):
            st.write("")

        if st.sidebar.button("Are you an admin? Log in here", use_container_width=True, key='admin_login_sidebar'):
            st.switch_page('pages/4_🔐_admin_login.py')

def show_login_page():

    show_user_info()

    st.title("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
                return
                
            with st.spinner("Logging in..."):
                success, error = login_user(email, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.success("Login successful!")
                    time.sleep(1)  # Give time for success message
                    st.switch_page("pages/3_💬_Chat.py")
                else:
                    st.error(f"Login failed: {error}")

if not st.session_state.get('authenticated', False):
    show_login_page()
else:
    st.success("You are already logged in!")
    if st.button("Go to Chat"):
        st.switch_page("pages/3_💬_Chat.py")