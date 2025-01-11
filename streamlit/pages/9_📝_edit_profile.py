import streamlit as st
from utils.auth import signup_user
from utils.auth_check import check_auth
import requests
import time

FLASK_URL = "http://127.0.0.1:5000"

check_auth()

# Hide sidebar and customize header
st.set_page_config(
    page_title="Edit Profile Page",
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
        st.markdown("### Chat")

        if st.button(f"💬 Chat", use_container_width=True):
            st.switch_page("pages/3_💬_chat.py")

        st.button(f"👤 {st.session_state.user_email}", use_container_width=True)

        # Add logout button with full width
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

def get_user_details():
    """Fetch user details from backend"""
    try:
        if not st.session_state.get('session'):
            st.error("Please login first")
            return None
        
        cookies = {'session': st.session_state.session}

        response = requests.get(
            f"{FLASK_URL}/users/me",
            cookies=cookies
        )

        if response.status_code == 200:
            return response.json()['user']
        else:
            st.error("Failed to fetch user details")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
    
def update_profile(user_id, data):
    """Update user profile"""
    try:
        if not st.session_state.get('session'):
            st.error("Please login first")
            return False
        
        cookies = {'session': st.session_state.session}

        response = requests.put(
            f"{FLASK_URL}/users/{user_id}",
            json=data,
            cookies=cookies
        )

        if response.status_code == 200:
            
            if 'email' in data:
                    st.session_state.user_email = data['email']

            st.success("Profile updated successfully")
            time.sleep(2)
            st.rerun()
            return True
        else:
            st.error("Failed to update profile")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False
    
def show_profile_page():

    show_user_info()

    st.title("Update Profile")

    user_details = get_user_details()

    if user_details:
        with st.form("update_profile_form"):
            email = st.text_input("Email", value=user_details.get('email', ''))
            username = st.text_input("Username", value=user_details.get('username', ''))
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            confirm_password = st.text_input("Confirm New Password", type='password')

            submit = st.form_submit_button("Update Profile")

            if submit:
                update_data = {
                    'email': email,
                    'username': username
                }

                if new_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                        return
                    update_data['password'] = new_password

                update_profile(user_details['id'], update_data)

if __name__ == "__main__":
        show_profile_page()