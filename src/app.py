import streamlit as st
from config import *
from auth import SessionManager
from components import *

# Must be the first Streamlit command to configure the page
st.set_page_config(
    page_title=APPLICATION_NAME + " - " + APPLICATION_TAGLINE,  # Title for the web page
    page_icon=APPLICATION_ICON,  # Icon for the web page
    layout="wide",  # Set the layout to wide (more spacious)
)

# Initialize session state to manage the session
SessionManager.init_session()

# Hide all Streamlit form-related elements like the helper text
st.markdown("""
    <style>
        /* Hide form submission helper text */
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

def show_welcome_screen():
    """
    Displays the welcome screen for the app. This includes the app name, description, tagline, and a prompt 
    to create a new analysis session. The user can click a button to initiate a new session.
    """
    st.markdown(
        f"""
        <div style='text-align: center; padding: 50px;'>
            <h1>{APPLICATION_ICON_EMOJI} {APPLICATION_NAME}</h1>
            <h3>{APPLICATION_DESCRIPTION}</h3>
            <p style='font-size: 1.2em; color: #666;'>{APPLICATION_TAGLINE}</p>
            <p>Start by creating a new analysis session</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        if st.button("➕ Create New Analysis Session", use_container_width=True, type="primary"):
            success, session = SessionManager.create_chat_session()  # Attempt to create a new chat session
            if success:
                st.session_state.current_session = session  # Store the session if created successfully
                st.rerun()  # Rerun the app to refresh the state
            else:
                st.error("Failed to create session")  # Show an error if session creation fails

def show_chat_history():
    """
    Displays the chat history for the current session. It fetches messages from the session 
    and displays them as either user or assistant messages.
    """
    # Fetch messages for the current session using the session ID
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session['id']
    )
    
    if success:
        # Iterate over the fetched messages and display them
        for msg in messages:
            if msg['role'] == 'user':
                st.info(msg['content'])  # User's message in an info style
            else:
                st.success(msg['content'])  # Assistant's message in a success style

def show_user_greeting():
    """
    Displays a greeting to the logged-in user. It fetches the user's name or email 
    and displays it at the top-right corner.
    """
    if st.session_state.user:
        # Get name from user data, fallback to email if name is empty
        display_name = st.session_state.user.get('name') or st.session_state.user.get('email', '')
        st.markdown(f"""
            <div style='text-align: right; padding: 1rem; color: #64B5F6; font-size: 1.1em;'>
                👋 Hi, {display_name}
            </div>
        """, unsafe_allow_html=True)

def main():
    """
    Main function to control the flow of the app. It manages user authentication, session creation,
    and the rendering of different pages based on the session state.
    """
    # Reinitialize session to ensure it's always fresh
    SessionManager.init_session()

    # Check if the user is authenticated; show login page if not
    if not SessionManager.is_authenticated():
        show_login_page()  # Show the login page
        show_footer()  # Show the footer for the app
        return

    # Show user greeting at the top
    show_user_greeting()
    
    # Show the sidebar containing navigation and session details
    show_sidebar()

    # Main chat area where chat history and analysis form are displayed
    if st.session_state.get('current_session'):
        st.title(f"📊 {st.session_state.current_session['title']}")  # Display the session title
        show_chat_history()  # Display chat history for the current session
        show_analysis_form()  # Display the analysis form for the current session
    else:
        show_welcome_screen()  # If no session exists, show the welcome screen

# This check ensures that main() is called only when the script is run directly
if __name__ == "__main__":
    main()