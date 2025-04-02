from config import ANALYSIS_DAILY_LIMIT
from components import show_footer
import streamlit as st
from auth import SessionManager

def show_sidebar():
    """
    Displays the sidebar of the application with options to:
    - Start a new analysis session
    - View the daily analysis limit
    - Show the list of previous sessions
    - Log out

    The sidebar also includes a footer component.
    """
    with st.sidebar:
        st.title("💬 Chat Sessions")
        
        # Button to start a new analysis session
        if st.button("+ New Analysis Session", use_container_width=True):
            if st.session_state.user and 'id' in st.session_state.user:
                success, session = SessionManager.create_chat_session()
                if success:
                    st.session_state.current_session = session
                    st.rerun()
                else:
                    st.error("Failed to create session")
            else:
                st.error("Please log in again")
                SessionManager.logout()
                st.rerun()

        # Add analysis counter display
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        
        # Calculate remaining analysis attempts for the day
        remaining = ANALYSIS_DAILY_LIMIT - st.session_state.analysis_count
        st.markdown(
            f"""
            <div style='
                padding: 0.5rem;
                border-radius: 0.5rem;
                background: rgba(100, 181, 246, 0.1);
                margin: 0.5rem 0;
                text-align: center;
                font-size: 0.9em;
            '>
                <p style='margin: 0; color: #666;'>Daily Analysis Limit</p>
                <p style='
                    margin: 0.2rem 0 0 0;
                    color: {"#1976D2" if remaining > 3 else "#FF4B4B"};
                    font-weight: 500;
                '>
                    {remaining}/{ANALYSIS_DAILY_LIMIT} remaining
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Horizontal separator
        st.markdown("---")
        show_session_list()
        
        # Logout button
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            SessionManager.logout()
            st.rerun()
        
        # Add footer to the sidebar
        show_footer(in_sidebar=True)

def show_session_list():
    """
    Fetches and displays the list of previous chat sessions for the logged-in user.

    If no sessions are found, it displays a message informing the user. Otherwise,
    it displays the list of sessions and allows the user to select a session to view.
    """
    if st.session_state.user and 'id' in st.session_state.user:
        success, sessions = SessionManager.get_user_sessions()
        if success:
            if sessions:
                st.subheader("Previous Sessions")
                render_session_list(sessions)
            else:
                st.info("No previous sessions")

def render_session_list(sessions):
    """
    Renders the list of sessions in the sidebar.

    Parameters:
    - sessions: List of session objects to display.
    """
    # Store deletion state in session state to track which session is being deleted
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = None
    
    for session in sessions:
        render_session_item(session)

def render_session_item(session):
    """
    Renders a single session item in the sidebar.

    Parameters:
    - session: The session dictionary that contains information about a session.
    """
    if not session or not isinstance(session, dict) or 'id' not in session:
        return
        
    session_id = session['id']
    current_session = st.session_state.get('current_session', {})
    current_session_id = current_session.get('id') if isinstance(current_session, dict) else None
    
    # Create a container for each session item
    with st.container():
        # Session title and delete button side by side
        title_col, delete_col = st.columns([4, 1])
        
        with title_col:
            if st.button(f"📝 {session['title']}", key=f"session_{session_id}", use_container_width=True):
                st.session_state.current_session = session
                st.rerun()
        
        with delete_col:
            # Button to delete the session
            if st.button("🗑️", key=f"delete_{session_id}", help="Delete this session"):
                if st.session_state.delete_confirmation == session_id:
                    st.session_state.delete_confirmation = None
                else:
                    st.session_state.delete_confirmation = session_id
                st.rerun()
        
        # Show confirmation to delete session if requested
        if st.session_state.delete_confirmation == session_id:
            st.warning("Delete above session?")
            left_btn, right_btn = st.columns(2)
            with left_btn:
                if st.button("Yes", key=f"confirm_delete_{session_id}", type="primary", use_container_width=True):
                    handle_delete_confirmation(session_id, current_session_id)
            with right_btn:
                if st.button("No", key=f"cancel_delete_{session_id}", use_container_width=True):
                    st.session_state.delete_confirmation = None
                    st.rerun()

def handle_delete_confirmation(session_id, current_session_id):
    """
    Handles the deletion of a session after the user confirms.

    Parameters:
    - session_id: The ID of the session to be deleted.
    - current_session_id: The ID of the currently active session (if any).
    """
    if not session_id:
        st.error("Invalid session")
        return
        
    # Delete the session using SessionManager
    success, error = SessionManager.delete_session(session_id)
    if success:
        st.session_state.delete_confirmation = None
        # Clear current session if the one being deleted was active
        if current_session_id and current_session_id == session_id:
            st.session_state.current_session = None
        st.rerun()
    else:
        st.error(f"Failed to delete: {error}")