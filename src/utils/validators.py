import re
from config import MAX_PDF_UPLOAD_SIZE_IN_MB

def validate_password(password):
    """
    Validate password meets security requirements.

    Args:
        password (str): The password string to validate.

    Returns:
        tuple: A tuple where the first element is a boolean indicating 
               whether the password is valid, and the second element is 
               an error message (if any).
    """
    # Check password length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check if password contains at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check if password contains at least one lowercase letter
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check if password contains at least one digit
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, None

def validate_email(email):
    """
    Validate email format using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, otherwise False.
    """
    # Regular expression to match a basic email format
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_signup_fields(name, email, password, confirm_password):
    """
    Validate all signup form fields including name, email, password, and 
    confirm password.

    Args:
        name (str): The user's name.
        email (str): The user's email address.
        password (str): The user's password.
        confirm_password (str): The user's confirmed password.

    Returns:
        tuple: A tuple where the first element is a boolean indicating 
               whether the fields are valid, and the second element is 
               an error message (if any).
    """
    # Check if all fields are filled in
    if not all([name, email, password, confirm_password]):
        return False, "Please fill in all fields"
    
    # Validate email format
    if not validate_email(email):
        return False, "Please enter a valid email address"
    
    # Check if passwords match
    if password != confirm_password:
        return False, "Passwords do not match"
    
    # Validate password security requirements
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
    
    return True, None

def validate_pdf_file(file):
    """
    Validate PDF file size and type.

    Args:
        file (file-like object): The uploaded PDF file to validate.

    Returns:
        tuple: A tuple where the first element is a boolean indicating 
               whether the file is valid, and the second element is 
               an error message (if any).
    """
    # Check if file is uploaded
    if not file:
        return False, "No file uploaded"
    
    # Check file size (convert size to MB)
    file_size_mb = file.size / (1024 * 1024)
    if file_size_mb > MAX_PDF_UPLOAD_SIZE_IN_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_PDF_UPLOAD_SIZE_IN_MB}MB limit"
    
    # Check if the file is a PDF
    if file.type != 'application/pdf':
        return False, "Invalid file type. Please upload a PDF file"
    
    return True, None

def validate_pdf_content(text):
    """
    Validate if the extracted PDF content appears to be a medical report.

    Args:
        text (str): The extracted text from the PDF file.

    Returns:
        tuple: A tuple where the first element is a boolean indicating 
               whether the content is valid, and the second element is 
               an error message (if any).
    """
    # List of common medical terms to check for
    medical_terms = [
        'blood', 'test', 'report', 'laboratory', 'lab', 'patient', 'specimen',
        'reference range', 'analysis', 'results', 'medical', 'diagnostic',
        'hemoglobin', 'wbc', 'rbc', 'platelet', 'glucose', 'creatinine'
    ]
    
    # Check if the text is sufficiently long
    if len(text.strip()) < 50:
        return False, "Extracted text is too short. Please ensure the PDF contains valid text."
    
    # Convert the text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Count how many medical terms appear in the text
    term_matches = sum(1 for term in medical_terms if term in text_lower)
    
    # Ensure at least 3 medical terms are found
    if term_matches < 3:
        return False, "The uploaded file doesn't appear to be a medical report. Please upload a valid medical report."
    
    return True, None