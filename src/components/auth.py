from config import *
import streamlit as st
from auth import SessionManager
import time
import re
from utils import validate_signup_fields

def show_login_page():
    """
    Displays the login or signup page based on the form type stored in the session state.
    
    The function displays the app's name, tagline, and description at the top, followed by
    either the login or signup form depending on the current form type. It also provides 
    a toggle button to switch between the login and signup forms.
    """
    # Initialize form_type session state if it doesn't exist
    if 'form_type' not in st.session_state:
        st.session_state['form_type'] = 'login'  # Default to 'login'
    
    # Get the current form type
    current_form = st.session_state['form_type']

    # Hide form submission helper text
    st.markdown("""
        <style>
            /* Hide form submission helper text */
            div[data-testid="InputInstructions"] > span:nth-child(1) {
                visibility: hidden;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display the app header with name, tagline, and description
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem; padding-top: 0;'>
            <h1>{APPLICATION_ICON_EMOJI} {APPLICATION_NAME}</h1>
            <h3>{APPLICATION_DESCRIPTION}</h3>
            <p style='font-size: 1.2em; color: #666; margin-bottom: 1em;'>{APPLICATION_TAGLINE}</p>
            <h3>{("Welcome Back!" if current_form == 'login' else "Welcome!")}</h3>
        </div>
    """, unsafe_allow_html=True)

    # Center the form in the layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Show the appropriate form (login or signup)
        if current_form == 'login':
            show_login_form()
        else:
            show_signup_form()
        
        # Toggle button to switch between login and signup forms
        st.markdown("---")
        toggle_text = "Don't have an account? Sign up" if current_form == 'login' else "Already have an account? Login"
        if st.button(toggle_text, use_container_width=True, type="secondary"):
            # Toggle form type in session state and reload the page
            st.session_state['form_type'] = 'signup' if current_form == 'login' else 'login'
            st.rerun()

def show_login_form():
    """
    Displays the login form where users can enter their email and password to log in.
    
    If the user provides valid login credentials, they will be logged in and redirected.
    Otherwise, an error message is shown.
    """
    with st.form("login_form"):
        # Input fields for email and password
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        # Login button
        if st.form_submit_button("Login", use_container_width=True, type="primary"):
            if email and password:
                # Attempt to login with the provided credentials
                success, result = SessionManager.login(email, password)
                if success:
                    # Show success message and redirect
                    with st.spinner("Logging in..."):
                        success_placeholder = st.empty()
                        success_placeholder.success("Login successful! Redirecting...")
                        time.sleep(1)  # Brief pause to show message
                        st.rerun()
                else:
                    st.error(f"Login failed: {result}")
            else:
                st.error("Please enter both email and password")

def show_signup_form():
    """
    Displays the signup form where new users can create an account by providing
    their full name, email, and password. The password must meet certain criteria.
    
    If the user successfully signs up, they will be redirected to the main app page.
    Otherwise, an error message is shown.
    """
    with st.form("signup_form"):
        # Input fields for name, email, password, and password confirmation
        new_name = st.text_input("Full Name", key="signup_name")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_password2")
        
        # Display password requirements
        st.markdown("""
            Password requirements:
            - At least 8 characters
            - One uppercase letter
            - One lowercase letter
            - One number
        """)
        
        # Sign up button
        if st.form_submit_button("Sign Up", use_container_width=True, type="primary"):
            # Validate the signup fields
            validation_result = validate_signup_fields(
                new_name, new_email, new_password, confirm_password
            )
            
            if not validation_result[0]:
                # Show error if validation fails
                st.error(validation_result[1])
                return
            
            # Show loading spinner during signup
            with st.spinner("Creating your account..."):
                success, response = st.session_state.auth_service.sign_up(
                    new_email, new_password, new_name
                )
                
                if success:
                    # On successful signup, authenticate the user and redirect
                    st.session_state.authenticated = True
                    st.session_state.user = response
                    st.success("Account created successfully! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    # Show error message if signup fails
                    st.error(f"Sign up failed: {response}")