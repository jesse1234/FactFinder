import streamlit as st

def show_user_info():
    """Display user information in sidebar"""
    with st.sidebar:
        st.markdown("### Navigation")

        if not st.session_state.authenticated:
            if st.sidebar.button("🔐 Login", use_container_width=True, key='login_sidebar'):
                st.switch_page('pages/1_🔐_login.py')
            
            if st.sidebar.button("📝 Sign Up", use_container_width=True, key='signup_sidebar'):
                st.switch_page('pages/2_📝_signup.py')
        else:
            if st.sidebar.button("💬 Chat", use_container_width=True, key='chat_sidebar'):
                st.switch_page('pages/3_💬_chat.py')

def main():
    st.set_page_config(
        page_title="News Fact Checker",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
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

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    show_user_info()

    # Main content container
    with st.container():
        st.title("Welcome to News Fact Checker")
        st.write("Your trusted source for fact-checking news and claims.")

        # Add some descriptive content
        st.markdown("""
        ### What We Offer
        - Real-time fact checking of news articles
        - Reliable source verification
        - Comprehensive analysis of claims
        - Evidence-based results
        """)

        # Create two columns for the buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            # Navigation buttons with styling
            st.markdown("### Get Started")
            if not st.session_state.authenticated:
                # Login button
                if st.button("Login", use_container_width=True):
                    st.switch_page("pages/1_🔐_login.py")
                
                # Add some spacing
                st.write("")
                
                # Sign Up button
                if st.button("Create Account", use_container_width=True):
                    st.switch_page("pages/2_📝_signup.py")
            else:
                # If already authenticated, show button to go to chat
                if st.button("Go to Chat", use_container_width=True):
                    st.switch_page("pages/3_💬_chat.py")

        # Add some information at the bottom
        st.markdown("---")
        st.markdown("""
        ### How It Works
        1. **Sign Up** or **Login** to your account
        2. Enter any news claim or article you want to verify
        3. Get comprehensive analysis with verified sources
        4. Make informed decisions based on facts
        """)

if __name__ == "__main__":
    main()