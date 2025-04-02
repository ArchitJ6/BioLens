import streamlit as st

def show_header():
    """
    Displays a personalized header message based on the logged-in user's information.
    
    If a user is logged in (i.e., `st.session_state.user` exists), the function retrieves
    the user's name (or email as a fallback) and displays a greeting message in the header. 
    The header is aligned to the right with a specific font color and size.

    The function ensures that the greeting message appears only if the user is authenticated.
    """
    if st.session_state.user:
        # Retrieve the user's name or use email as a fallback
        display_name = st.session_state.user.get('name') or st.session_state.user.get('email', '')
        
        # Display the greeting message
        st.markdown(f"""
            <div style='text-align: right; padding: 1rem; color: #64B5F6; font-size: 1.1em;'>
                👋 Hi, {display_name}
            </div>
        """, unsafe_allow_html=True)