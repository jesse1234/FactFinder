import streamlit as st 
import pandas as pd 
import requests
from utils.auth_check import admin_check_auth

FLASK_URL = 'http://127.0.0.1:5000'

st.set_page_config(
    page_title='User Management',
    page_icon='👥',
    layout='wide',
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

        st.markdown("### User Table")

        st.empty()
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        if st.button(f"💬 Chat", use_container_width=True):
            st.switch_page("pages/5_💬_admin_chat.py")

        if st.sidebar.button("Query Logs", use_container_width=True, key='query_logs'):
            st.switch_page('pages/8_📝_query_logs.py')

        if st.sidebar.button("Edit Profile", use_container_width=True, key='query_logs'):
            st.switch_page('pages/10_📝_admin_edit_profile.py')

        st.button(f"👤 {st.session_state.user_email}", use_container_width=True)

        # Add logout button with full width
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

admin_check_auth()

def get_users():
    """Fetch users from backend"""
    try: 
        if not st.session_state.get('session'):
            st.error("Please login first")
            return []
        
        cookies = {'session': st.session_state.session}
        
        response = requests.get(f"{FLASK_URL}/users", cookies=cookies)
        if response.status_code == 200:
            return response.json()['users']
        else:
            st.error("Failed to fetch users")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def delete_user(user_id):
    """Delete user"""
    try:
        cookies = {'session': st.session_state.session}
        response = requests.delete(
            f"{FLASK_URL}/users/{user_id}",
            cookies=cookies
        )
        if response.status_code == 200:
            st.success("User deleted successfully")
            st.rerun()
        else:
            st.error("Failed to delete user")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def update_user(user_id, data):
    """Update user"""
    try:
        cookies = {'session': st.session_state.session}
        response = requests.put(
            f"{FLASK_URL}/users/{user_id}",
            json=data,
            cookies=cookies
        )
        if response.status_code == 200:
            st.success('User updated successfully')
            st.rerun()
        else:
            st.error("Failed to update user")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_user_table():

    show_user_info()
    
    st.title("User Management")

    search_query = st.text_input("🔍 Search Users", "")

    users = get_users()

    if search_query:
        users = [user for user in users if
                 search_query.lower() in user['email'].lower() or
                 search_query.lower() in user['username'].lower()]
        
    if users:
        df = pd.DataFrame(users)

        # Create the table with edit and delete buttons
        st.write("### Users Table")
        
        # Create a table with columns for data and actions
        cols = st.columns([3, 2, 1, 1])  # Adjust column widths as needed
        
        # Table headers
        cols[0].write("**Email**")
        cols[1].write("**Username**")
        cols[2].write("**Edit**")
        cols[3].write("**Delete**")
        
        # Table rows
        for index, row in df.iterrows():
            cols = st.columns([3, 2, 1, 1])
            
            # Data columns
            cols[0].write(row['email'])
            cols[1].write(row['username'])
            
            # Delete button with confirmation
            if cols[3].button("🗑️", key=f"delete_{row['id']}", type="primary"):
                if cols[3].button("Confirm", key=f"confirm_{row['id']}", type="primary"):
                    delete_user(row['id'])
            
            st.markdown("---")  # Add separator between rows

        # Export option
        st.download_button(
            "📥 Export Users",
            df.to_csv(index=False).encode('utf-8'),
            "users.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No users found")

if __name__ == "__main__":
    show_user_table()