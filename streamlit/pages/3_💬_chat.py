import streamlit as st
import requests
from utils.auth_check import check_auth
import json

FLASK_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Chat Page",
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

check_auth()

def show_user_info():
    """Display user information in sidebar"""
    with st.sidebar:
        st.markdown("### Chat History")
        
        # New Chat button
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        if not st.session_state.get('session'):
            return
        
        cookies = {'session': st.session_state.session}
        response = requests.get(f"{FLASK_URL}/users/chat/history", cookies=cookies)

        if response.status_code == 200:
            histories = response.json()['histories']

            for history in histories:
                if st.button(
                    f"💬 {history['title']}...",
                    key=f"history_{history['id']}",
                    use_container_width=True
                ):
                    st.session_state.messages = history['messages']
                    st.session_state.current_chat_id = history['id']  # Store the chat ID
                    st.rerun()

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

        if st.button(f"Edit Profile", use_container_width=True):
            st.switch_page("pages/9_📝_edit_profile.py")

        st.button(f"👤 {st.session_state.user_email}", use_container_width=True)

        # Add logout button with full width
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

def format_json_response(json_str):
    """Format JSON response into readable text"""
    try:
        # If the string is already a dict, use it directly
        if isinstance(json_str, dict):
            data = json_str
        else:
            # Try to parse the string as JSON
            data = json.loads(json_str.replace("'", '"'))
        
        formatted_text = ""
        
        # Order of sections
        sections = [
            "Summary of Findings",
            "Cross-Verification",
            "Contextual Background",
            "Conclusion",
            "Verdict",
            "References"
        ]
        
        # Add each section if it exists
        for section in sections:
            if section + ":" in data:
                formatted_text += f"**{section}:**\n"
                content = data[section + ":"]
                # Handle references differently if they're in a list
                if isinstance(content, list):
                    formatted_text += "\n".join(content)
                else:
                    formatted_text += str(content)
                formatted_text += "\n\n"
        
        return formatted_text
    except Exception as e:
        print(f"Error formatting JSON: {str(e)}")
        return str(json_str)
    

def save_current_chat():
    """Save current chat to history"""
    try:
        if not st.session_state.messages:
            return
        
        cookies = {'session': st.session_state.session}
        
        # Get the first message content for title
        first_message = next((msg for msg in st.session_state.messages if msg['role'] == 'user'), None)
        title = first_message['content'][:50] if first_message else "New Chat"
        
        current_chat_id = st.session_state.get('current_chat_id')
        
        response = requests.post(
            f"{FLASK_URL}/users/chat/history",
            json={
                'messages': st.session_state.messages,
                'session_id': current_chat_id,
                'title': title
            },
            cookies=cookies
        )

        if response.status_code == 200:
            if not current_chat_id:  # Only update if this is a new chat
                st.session_state.current_chat_id = response.json()['history_id']
                
    except Exception as e:
        st.error(f"Error saving chat: {str(e)}")


def show_chat_interface():
    st.title("News Fact Checker Chat")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None

    show_user_info()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Format the output if it's from the assistant
                st.markdown(format_json_response(message["content"]))
            else:
                st.write(message["content"])
            
            if "sources" in message:
                with st.expander("View Sources"):
                    st.write(message["sources"])
    
    if prompt := st.chat_input("What would you like to fact-check?"):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Checking facts..."):
                try:
                    # Create session with cookie
                    if not st.session_state.get('session'):
                        st.error("Session expired. Please login again")
                        st.session_state.authenticated = False
                        st.rerun()

                    cookies = {'session': st.session_state.session}

                    response = requests.post(
                        f"{FLASK_URL}/rag/process-query",
                        json={'query': prompt},
                        cookies=cookies
                    )

                    # session = requests.Session()
                    # if st.session_state.get('session_token'):
                    #     session.cookies.set('session', st.session_state.session_token)
                    
                    # response = session.post(
                    #     f"{FLASK_URL}/rag/process-query",
                    #     json={"query": prompt},
                    # )
                    
                    if response.status_code == 200:
                        data = response.json()

                        formatted_output = format_json_response(data['output'])
                        st.write(formatted_output)
                        
                        message_data = {
                            "role": "assistant",
                            "content": data["output"]
                        }
                        
                        if "context" in data:
                            with st.expander("View Sources"):
                                st.write(data["context"])
                            message_data["sources"] = data["context"]
                        
                        st.session_state.messages.append(message_data)
                    elif response.status_code == [401, 302]:  # Redirect to login
                        st.error("Session expired. Please login again.")
                        st.session_state.authenticated = False
                        st.rerun()
                    else:
                        st.error(f"Failed to process your request. Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    if st.session_state.messages:
        save_current_chat()

# Show interface
if st.session_state.get('authenticated', False):
    show_chat_interface()
else:
    st.error("Please login to access the chat.")
    if st.button("Go to Login"):
        st.switch_page("pages/1_🔐_login.py")