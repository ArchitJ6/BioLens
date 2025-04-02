import streamlit as st
from agents.analysisAgent import AnalysisAgent

def init_analysis_state():
    """
    Initializes the session state for the analysis agent if not already initialized.
    
    This function ensures that the 'analysis_agent' object is available in the session state.
    If it doesn't exist, it creates a new instance of the AnalysisAgent class.
    """
    if 'analysis_agent' not in st.session_state:
        st.session_state.analysis_agent = AnalysisAgent()

def check_rate_limit():
    """
    Checks if the user has reached their daily analysis limit.
    
    This function ensures that the analysis agent is initialized before checking the rate limit.
    
    Returns:
        tuple: A tuple containing a boolean indicating if the user can analyze 
               and an optional error message.
    """
    # Ensure the analysis agent is initialized before checking rate limits
    init_analysis_state()
    return st.session_state.analysis_agent.check_rate_limit()

def generate_analysis(data, system_prompt, check_only=False, session_id=None):
    """
    Generates an analysis report if the user is within their rate limits.
    
    This function will either check the rate limits or generate an analysis, 
    based on the value of `check_only`.
    
    Args:
        data (dict): The data (such as patient report) to analyze.
        system_prompt (str): The system's prompt for guiding the analysis.
        check_only (bool): If True, only checks the rate limit without generating analysis.
        session_id (str, optional): The session ID used for retrieving chat history (default is None).
        
    Returns:
        dict: A dictionary with the analysis result or the rate limit check result.
    """
    # Ensure the analysis agent is initialized before performing analysis
    init_analysis_state()
    
    # If check_only is True, only check the rate limit without generating analysis
    if check_only:
        return st.session_state.analysis_agent.check_rate_limit()
    
    # For now, we're not passing chat_history due to issues in handling it
    # The commented code below outlines how it could be handled if chat_history was necessary.
    # chat_history = None
    # if session_id and 'auth_service' in st.session_state:
    #     success, messages = st.session_state.auth_service.get_session_messages(session_id)
    #     if success:
    #         chat_history = messages
    
    # Call the analyze_report method from the analysis agent, without chat_history for now
    return st.session_state.analysis_agent.analyze_report(
        data=data,
        system_prompt=system_prompt,
        check_only=False  # Only set check_only as False here to actually generate the analysis
    )