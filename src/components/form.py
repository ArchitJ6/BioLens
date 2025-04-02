import streamlit as st
from agents import generate_analysis
from config import PROMPTS
from utils import extract_text_from_pdf
from config import SAMPLE_REPORT
from config import MAX_PDF_UPLOAD_SIZE_IN_MB

def show_analysis_form():
    """
    Displays the form to upload a PDF or use a sample report and triggers the analysis of the report.
    
    The form allows the user to choose between uploading a custom PDF or using a sample PDF. 
    Once the report content is available, it displays a patient information form and 
    triggers the analysis process when submitted.
    """
    # Initialize report source in session state for new sessions
    if 'current_session' in st.session_state and 'report_source' not in st.session_state:
        st.session_state.report_source = "Upload PDF"
    
    # Radio button to choose between uploading a PDF or using a sample PDF
    report_source = st.radio(
        "Choose report source",
        ["Upload PDF", "Use Sample PDF"],
        index=0 if st.session_state.get('report_source') == "Upload PDF" else 1,
        horizontal=True,
        key='report_source'
    )

    # Fetch the report contents based on the selected source
    pdf_contents = get_report_contents(report_source)
            
    if pdf_contents:  # Only show the patient form if the report contents are available
        render_patient_form(pdf_contents)

def get_report_contents(report_source):
    """
    Retrieves the contents of the report based on the selected source: either uploading a PDF or using a sample report.
    
    Parameters:
    - report_source: The selected source for the report, either "Upload PDF" or "Use Sample PDF".
    
    Returns:
    - pdf_contents: The extracted text content from the uploaded PDF or the sample report content.
    """
    if report_source == "Upload PDF":
        # Display file uploader to upload a PDF
        uploaded_file = st.file_uploader(
            f"Upload blood report PDF (Max {MAX_PDF_UPLOAD_SIZE_IN_MB}MB)", 
            type=['pdf'],
            help=f"Maximum file size: {MAX_PDF_UPLOAD_SIZE_IN_MB}MB. Only PDF files containing medical reports are supported"
        )
        
        if uploaded_file:
            # Check file size before processing
            file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert to MB
            if file_size_mb > MAX_PDF_UPLOAD_SIZE_IN_MB:
                st.error(f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_PDF_UPLOAD_SIZE_IN_MB}MB limit.")
                return None

            if uploaded_file.type != 'application/pdf':
                st.error("Please upload a valid PDF file.")
                return None
                
            # Extract text from the uploaded PDF
            pdf_contents = extract_text_from_pdf(uploaded_file)
            
            # Check for errors in the extracted PDF content
            if isinstance(pdf_contents, str) and (
                pdf_contents.startswith(("File size exceeds", "Invalid file type", "Error validating")) or
                pdf_contents.startswith("The uploaded file") or
                "error" in pdf_contents.lower()
            ):
                st.error(pdf_contents)
                return None
            
            # Show the extracted PDF content in an expandable view
            with st.expander("View Extracted Report"):
                st.text(pdf_contents)
            return pdf_contents
    else:
        # If using a sample report, display it in an expandable view
        with st.expander("View Sample Report"):
            st.text(SAMPLE_REPORT)
        return SAMPLE_REPORT
    return None

def render_patient_form(pdf_contents):
    """
    Renders the patient information form for analyzing the uploaded report.
    
    Parameters:
    - pdf_contents: The extracted content from the PDF report to be analyzed.
    
    Displays form fields for patient name, age, and gender and triggers report analysis when submitted.
    """
    with st.form("analysis_form"):
        # Input fields for patient name, age, and gender
        patient_name = st.text_input("Patient Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        # Submit button to trigger the analysis
        if st.form_submit_button("Analyze Report"):
            handle_form_submission(patient_name, age, gender, pdf_contents)

def handle_form_submission(patient_name, age, gender, pdf_contents):
    """
    Handles the form submission to start the analysis process.
    
    Parameters:
    - patient_name: The name of the patient to analyze the report for.
    - age: The age of the patient.
    - gender: The gender of the patient.
    - pdf_contents: The extracted content from the report to analyze.
    
    Checks if the form is complete, then generates the analysis and saves chat messages.
    """
    if not all([patient_name, age, gender]):
        st.error("Please fill in all fields")
        return

    # Check rate limit before proceeding with the analysis
    can_analyze, error_msg = generate_analysis(None, None, check_only=True)
    if not can_analyze:
        st.error(error_msg)
        st.stop()
        return

    with st.spinner("Analyzing report..."):
        # Save user message indicating the report is being analyzed
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session['id'],
            f"Analyzing report for patient: {patient_name}"
        )
        
        # Generate the analysis based on patient data and report content
        result = generate_analysis({
            "patient_name": patient_name,
            "age": age,
            "gender": gender,
            "report": pdf_contents
        }, PROMPTS["comprehensive_analyst"])
        
        if result["success"]:
            # Add model used information if available
            content = result["content"]
            if "model_used" in result:
                model_info = f"\n\n*Analysis generated using {result['model_used']}*"
                content += model_info
                
            # Save the analysis response and rerun the app
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session['id'],
                content,
                role='assistant'
            )
            st.rerun()
        else:
            st.error(result["error"])
            st.stop()