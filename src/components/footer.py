from config import PRIMARY_COLOR, SECONDARY_COLOR
import streamlit as st

def show_footer(in_sidebar=False):
    """
    Displays the footer of the app. The footer includes a credit to the creator, 
    and adjusts its layout based on whether it is shown in the sidebar or in the main view.

    The footer's background uses a gradient style, and the credit text is styled with a hover effect 
    that changes the link color and text decoration.

    Parameters:
        in_sidebar (bool): A flag to indicate if the footer is being displayed in the sidebar (True) 
                            or in the main content area (False). Adjusts the margin-top and width of the footer.
    """
    # Define base styles for the footer, which can change based on whether it's in the sidebar or the main view
    base_styles = f"""
        text-align: center;
        padding: 0.5rem;
        background: linear-gradient(to right, rgba(25, 118, 210, 0.02), rgba(100, 181, 246, 0.05), rgba(25, 118, 210, 0.02));
        border-top: 1px solid rgba(100, 181, 246, 0.1);
        margin-top: {'0' if in_sidebar else '2rem'};  # No top margin in the sidebar, some margin in the main view
        {'width: 100%' if not in_sidebar else ''};  # Full width for main view, adjust as needed for sidebar
    """
    
    # Render the footer content using markdown with embedded HTML and styling
    st.markdown(
        f"""
        <div style='{base_styles}'>
            <p style='
                font-family: "Source Sans Pro", sans-serif;
                color: #64B5F6;
                font-size: 1rem;
                letter-spacing: 0.02em;
                margin: 0;
                opacity: 0.9;
                text-align: center;
            '>
                Created by 
                <a href='https://architj6.xyz/' 
                    target='_blank' 
                    style='
                        color: #1976D2;
                        text-decoration: none;
                        font-weight: 500;
                        transition: all 0.2s ease;
                    '
                    onmouseover="this.style.color='{SECONDARY_COLOR}'; this.style.textDecoration='underline';"
                    onmouseout="this.style.color='#1976D2'; this.style.textDecoration='none';">
                    Archit Jain ❤️
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True  # Allow rendering HTML content in Streamlit
    )