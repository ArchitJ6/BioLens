import pdfplumber
import streamlit as st
from config import MAX_PDF_PAGE_COUNT
from utils.validators import validate_pdf_file, validate_pdf_content

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file, validates the file and content, and returns the extracted text or an error message.

    Args:
        pdf_file (file-like object): The PDF file to extract text from.

    Returns:
        str: The extracted text from the PDF or an error message if something goes wrong.
    """
    try:
        # Step 1: Validate the PDF file before extraction
        is_valid, error = validate_pdf_file(pdf_file)
        if not is_valid:
            return error  # Return validation error if the file is invalid

        text = ""  # Initialize an empty string to store the extracted text
        
        # Step 2: Open and read the PDF using pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            # Check if the number of pages in the PDF exceeds the maximum allowed
            if len(pdf.pages) > MAX_PDF_PAGE_COUNT:
                return f"PDF exceeds maximum page limit of {MAX_PDF_PAGE_COUNT}"
            
            # Step 3: Extract text from each page of the PDF
            for page in pdf.pages:
                extracted = page.extract_text()
                
                # Append the extracted text from this page to the full text
                text += extracted + "\n"

        # Remove any leading or trailing whitespace from the extracted text
        if text.replace("\n", "") == "":
            # If the extracted text is empty, return an error message
            raise ValueError("Could not extract text from PDF. Please ensure it's not a scanned document.")
        
        # Step 4: Validate the extracted text content
        is_valid, error = validate_pdf_content(text)
        if not is_valid:
            return error  # Return validation error if the content is invalid
            
        return text  # Return the successfully extracted text from the PDF
        
    except Exception as e:
        # Return a general error message if something goes wrong during the extraction process
        return f"Error extracting text from PDF: {str(e)}"