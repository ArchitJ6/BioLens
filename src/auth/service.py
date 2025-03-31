import streamlit as st
from datetime import datetime
import time
import re
from st_supabase_connection import SupabaseConnection
from auth.session import SessionManager

class AuthService:
    """
    Handles user authentication, session management, and chat message storage.
    Interacts with Supabase services for user authentication, data storage, 
    and retrieval of chat messages and sessions.
    """

    def __init__(self):
        """
        Initializes the AuthService class by establishing a connection to 
        the Supabase service and validating the session token if present.
        """
        try:
            # Custom connection parameters for Supabase
            self.supabase = st.connection(
                "supabase",
                type=SupabaseConnection,
                ttl=None,
                url=st.secrets["SUPABASE_URL"],
                key=st.secrets["SUPABASE_KEY"],
                client_options={
                    "timeout": 30,  # 30 seconds timeout
                    "retries": 3,   # 3 retries
                }
            )
        except Exception as e:
            st.error(f"Failed to initialize services: {str(e)}")
            raise e
        
        # Validate session on initialization
        if 'auth_token' in st.session_state:
            if not self.validate_session_token():
                self.sign_out()

    def validate_email(self, email):
        """
        Validates the email format using a regular expression.

        Args:
            email (str): The email to validate.

        Returns:
            bool: True if the email format is valid, otherwise False.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def check_existing_user(self, email):
        """
        Checks if a user with the provided email already exists in the database.

        Args:
            email (str): The email to check.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        try:
            result = self.supabase.table('users')\
                .select('id')\
                .eq('email', email)\
                .execute()
            return len(result.data) > 0
        except Exception:
            return False

    def sign_up(self, email, password, name):
        """
        Signs up a new user with the provided email, password, and name.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.
            name (str): The name of the user.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message or user data.
        """
        try:
            # Create a new user in Supabase authentication system
            auth_response = self.supabase.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if not auth_response.user:
                return False, "Failed to create user account"
            
            # Store user data in the 'users' table
            user_data = {
                'id': auth_response.user.id,
                'email': email,
                'name': name,
                'created_at': datetime.now().isoformat()
            }
            self.supabase.table('users').insert(user_data).execute()
            
            return True, user_data
                
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate" in error_msg or "already registered" in error_msg:
                return False, "Email already registered"
            return False, f"Sign up failed: {str(e)}"

    def sign_in(self, email, password):
        """
        Signs in an existing user using their email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message or user data.
        """
        try:
            # Clear any existing session data first
            self.sign_out()
            
            # Authenticate the user with Supabase
            auth_response = self.supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response and auth_response.user:
                # Get user data
                user_data = self.get_user_data(auth_response.user.id)
                if not user_data:
                    return False, "User data not found"
                    
                # Store session information in Streamlit session state
                st.session_state.auth_token = auth_response.session.access_token
                st.session_state.user = user_data
                return True, user_data
                
            return False, "Invalid login response"
        except Exception as e:
            return False, str(e)
    
    def sign_out(self):
        """
        Signs out the current user by clearing session data.

        Returns:
            tuple: A tuple containing a boolean indicating success and any error message.
        """
        try:
            self.supabase.client.auth.sign_out()
            SessionManager.clear_session_state()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_user(self):
        """
        Retrieves the current user from Supabase based on the session token.

        Returns:
            dict: The user data if found, otherwise None.
        """
        try:
            return self.supabase.client.auth.get_user()
        except Exception:
            return None

    def create_session(self, user_id, title=None):
        """
        Creates a new chat session for the user.

        Args:
            user_id (str): The ID of the user.
            title (str, optional): The title of the session. Defaults to None.

        Returns:
            tuple: A tuple containing a boolean indicating success and the session data or error message.
        """
        try:
            current_time = datetime.now()
            default_title = f"{current_time.strftime('%d-%m-%Y')} | {current_time.strftime('%H:%M:%S')}"
            
            session_data = {
                'user_id': user_id,
                'title': title or default_title,
                'created_at': current_time.isoformat()
            }
            result = self.supabase.table('chat_sessions').insert(session_data).execute()
            return True, result.data[0] if result.data else None
        except Exception as e:
            return False, str(e)

    def get_user_sessions(self, user_id):
        """
        Retrieves the list of chat sessions associated with the given user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            tuple: A tuple containing a boolean indicating success and the session data or error message.
        """
        try:
            result = self.supabase.table('chat_sessions')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
            return True, result.data
        except Exception as e:
            st.error(f"Error fetching sessions: {str(e)}")
            return False, []

    def save_chat_message(self, session_id, content, role='user'):
        """
        Saves a new chat message to the database.

        Args:
            session_id (str): The session ID where the message belongs.
            content (str): The content of the message.
            role (str, optional): The role of the sender (e.g., 'user', 'admin'). Defaults to 'user'.

        Returns:
            tuple: A tuple containing a boolean indicating success and the saved message data or error message.
        """
        try:
            message_data = {
                'session_id': session_id,
                'content': content,
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            result = self.supabase.table('chat_messages').insert(message_data).execute()
            return True, result.data[0] if result.data else None
        except Exception as e:
            return False, str(e)

    def get_session_messages(self, session_id):
        """
        Retrieves all messages for a given session.

        Args:
            session_id (str): The ID of the session.

        Returns:
            tuple: A tuple containing a boolean indicating success and the list of messages or error message.
        """
        try:
            result = self.supabase.table('chat_messages')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at')\
                .execute()
            return True, result.data
        except Exception as e:
            return False, str(e)

    def delete_session(self, session_id):
        """
        Deletes a chat session and all its associated messages.

        Args:
            session_id (str): The ID of the session to delete.

        Returns:
            tuple: A tuple containing a boolean indicating success and any error message.
        """
        try:
            # Delete all messages for the session
            self.supabase.table('chat_messages')\
                .delete()\
                .eq('session_id', session_id)\
                .execute()

            # Delete the session itself
            self.supabase.table('chat_sessions')\
                .delete()\
                .eq('id', session_id)\
                .execute()

            return True, None
        except Exception as e:
            st.error(f"Failed to delete session: {str(e)}")
            return False, str(e)
    
    def validate_session_token(self):
        """
        Validates the existing session token to ensure it is still valid.

        Returns:
            dict: User data if the session token is valid, otherwise None.
        """
        try:
            session = self.supabase.client.auth.get_session()
            if not session or not session.access_token:
                return None
                
            # Verify token matches stored token
            if session.access_token != st.session_state.get('auth_token'):
                return None
                
            user = self.supabase.client.auth.get_user()
            if not user or not user.user:
                return None
                
            return self.get_user_data(user.user.id)
        except Exception:
            return None
    
    def get_user_data(self, user_id):
        """
        Retrieves user data from the database.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: User data if found, otherwise None.
        """
        try:
            response = self.supabase.table('users')\
                .select('*')\
                .eq('id', user_id)\
                .single()\
                .execute()
            return response.data if response else None
        except Exception:
            return None