import streamlit as st 
import pandas as pd 
import requests
from utils.auth_check import admin_check_auth

FLASK_URL = 'http://127.0.0.1:5000'

st.set_page_config(
    page_title='Query Management',
    page_icon='🔍',
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
    </style>
""", unsafe_allow_html=True)

admin_check_auth()

def show_user_info():
    """Display user information in sidebar"""
    with st.sidebar:
        st.markdown("### Chat")

        if st.sidebar.button("User Table", use_container_width=True, key='user_table'):
            st.switch_page('pages/7_📝_user_table.py')

        if st.sidebar.button("Query Logs", use_container_width=True, key='query_logs'):
            st.switch_page('pages/8_📝_query_logs.py')

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
        st.write("")
        st.write("")
        st.write("")

        st.button(f"👤 {st.session_state.user_email}", use_container_width=True)

        # Add logout button with full width
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

def get_queries():
    """Fetch queries from backend"""
    try: 
        if not st.session_state.get('session'):
            st.error("Please login first")
            return []
        
        cookies = {'session': st.session_state.session}
        
        response = requests.get(f"{FLASK_URL}/queries", cookies=cookies)
        if response.status_code == 200:
            return response.json()['queries']
        else:
            st.error("Failed to fetch queries")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def delete_query(query_id):
    """Delete query"""
    try:
        cookies = {'session': st.session_state.session}
        response = requests.delete(
            f"{FLASK_URL}/queries/{query_id}",
            cookies=cookies
        )
        if response.status_code == 200:
            st.success("Query deleted successfully")
            st.rerun()
        else:
            st.error("Failed to delete query")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def format_json_response(json_str):
    """Format JSON response into readable text"""
    try:
        if isinstance(json_str, str):
            # Remove single quotes and escape characters
            json_str = json_str.replace("'", '"').replace("\\", "")
        
        return json_str
    except Exception as e:
        print(f"Error formatting JSON: {str(e)}")
        return str(json_str)

def show_query_table():

    show_user_info()
    
    st.title("Query Management")

    search_query = st.text_input("🔍 Search Queries", "")

    queries = get_queries()

    if search_query:
        queries = [query for query in queries if
                  search_query.lower() in query['question'].lower() or
                  search_query.lower() in query['output'].lower()]
        
    if queries:
        df = pd.DataFrame(queries)

        # Create the table with query details and delete button
        st.write("### Queries Table")
        
        # Create a table with columns for data and actions
        cols = st.columns([2, 3, 2, 1, 1])  # Adjust column widths as needed
        
        # Table headers
        cols[0].write("**Query**")
        cols[1].write("**Output**")
        cols[2].write("**Date**")
        cols[3].write("**User ID**")
        cols[4].write("**Delete**")
        
        # Table rows
        for index, row in df.iterrows():
            cols = st.columns([2, 3, 2, 1, 1])
            
            # Data columns
            cols[0].write(row['question'])  # Changed from 'query' to 'question'
            
            # Format and display output in an expander
            with cols[1].expander("View Output"):
                st.write(format_json_response(row['output']))
            
            # Format and display date
            cols[2].write(row['date'])
            cols[3].write(str(row['user_id']))
            
            st.markdown("---")  
    else:
        st.info("No queries found")

if __name__ == "__main__":
    show_query_table()