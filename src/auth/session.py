from auth.service import AuthService
from config import SESSION_TIMEOUT_IN_MINUTES
from datetime import datetime, timedelta
import streamlit as st

class SessionManager:
    """
    Manages user sessions, including initialization, validation, creation, deletion, 
    and authentication checks. It ensures session integrity and handles timeouts.

    This class utilizes Streamlit's session state to store session variables like 
    authentication status, user data, and activity timestamps.
    """

    @staticmethod
    def init_session():
        """
        Initializes or validates the user session.

        This method ensures that the session is properly initialized, verifies the 
        user's authentication status, and checks for session timeouts. It also 
        initializes required services, such as authentication, and updates the 
        session's last activity timestamp.

        If the session has timed out, the session state is cleared, and the user 
        is prompted to log in again.

        Raises:
            None

        Returns:
            None
        """
        # Clear all session state variables if it's a new browser session
        if 'session_initialized' not in st.session_state:
            SessionManager.clear_session_state()
            st.session_state.session_initialized = True
            
        # Initialize the auth service if not already done
        if 'auth_service' not in st.session_state:
            st.session_state.auth_service = AuthService()
        
        # Check if the session has timed out
        if 'last_activity' in st.session_state:
            idle_time = datetime.now() - st.session_state.last_activity
            if idle_time > timedelta(minutes=SESSION_TIMEOUT_IN_MINUTES):
                SessionManager.clear_session_state()
                st.error("Session expired. Please log in again.")
                st.rerun()
        
        # Update the last activity time
        st.session_state.last_activity = datetime.now()
        
        # Validate the session token if user is logged in
        if 'user' in st.session_state:
            user_data = st.session_state.auth_service.validate_session_token()
            if not user_data:
                SessionManager.clear_session_state()
                st.error("Invalid session. Please log in again.")
                st.rerun()

    @staticmethod
    def clear_session_state():
        """
        Clears the session state variables.

        This method clears all session state variables except for the 'session_initialized'
        key, which prevents re-initializing the session on each page load. This method 
        is used when initializing a new session or when the user logs out.

        Raises:
            None

        Returns:
            None
        """
        keys_to_keep = ["session_initialized"]
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]

    @staticmethod
    def is_authenticated():
        """
        Checks if the user is authenticated.

        This method checks whether the 'user' key exists in the session state, indicating
        that the user is logged in.

        Returns:
            bool: True if the user is authenticated, otherwise False.
        """
        return bool(st.session_state.get("user"))
    
    @staticmethod
    def create_chat_session():
        """
        Creates a new chat session for the authenticated user.

        This method attempts to create a new chat session by calling the authentication 
        service's `create_session` method with the user's ID. It returns a tuple 
        indicating success or failure and an optional message.

        Returns:
            tuple: A tuple where the first element is a boolean indicating success,
                   and the second element is either a message or session data.
        """
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        return st.session_state.auth_service.create_session(
            st.session_state.user['id']
        )
    
    @staticmethod
    def get_user_sessions():
        """
        Retrieves the user's chat sessions.

        This method fetches the list of chat sessions associated with the authenticated
        user by calling the authentication service's `get_user_sessions` method.
        It returns a tuple containing a boolean and either a list of sessions or an error message.

        Returns:
            tuple: A tuple where the first element is a boolean indicating success, 
                   and the second element is a list of sessions or an empty list if no sessions exist.
        """
        if not SessionManager.is_authenticated():
            return False, []
        return st.session_state.auth_service.get_user_sessions(
            st.session_state.user['id']
        )
    
    @staticmethod
    def delete_session(session_id):
        """
        Deletes a specific chat session.

        This method attempts to delete a chat session by calling the authentication 
        service's `delete_session` method with the provided session ID. It returns a 
        tuple indicating success or failure and an optional message.

        Args:
            session_id (str): The ID of the chat session to delete.

        Returns:
            tuple: A tuple where the first element is a boolean indicating success, 
                   and the second element is a message or error if the session can't be deleted.
        """
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        return st.session_state.auth_service.delete_session(session_id)
    
    @staticmethod
    def logout():
        """
        Logs the user out and clears the session.

        This method signs out the user using the authentication service and then 
        clears all session state variables, effectively logging out the user.

        Returns:
            None
        """
        if 'auth_service' in st.session_state:
            st.session_state.auth_service.sign_out()
        SessionManager.clear_session_state()

    @staticmethod
    def login(email, password):
        """
        Handles user login by authenticating with the provided email and password.

        This method authenticates the user using the authentication service and 
        stores the resulting authentication data in the session state.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            tuple: A tuple containing a boolean indicating success and an optional 
                   message or authentication data if login is successful.
        """
        if 'auth_service' not in st.session_state:
            st.session_state.auth_service = AuthService()
            
        return st.session_state.auth_service.sign_in(email, password)