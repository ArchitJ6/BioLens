# Basic Application Configuration
APPLICATION_NAME = "BioLens"
APPLICATION_TAGLINE = "The AI Lens for Your Health"
APPLICATION_ICON = ":dna:"
APPLICATION_ICON_EMOJI = "🧬"
APPLICATION_DESCRIPTION = "An AI-powered health insights tool that analyzes blood reports, detects potential risks, and provides personalized medical recommendations. 🚀🔬"
APPLICATION_VERSION = "1.0.0"

# Initial Configuration
MAX_PDF_UPLOAD_SIZE_IN_MB = 20 # Maximum PDF upload size in MB
MAX_PDF_PAGE_COUNT = 50 # Maximum number of pages in the PDF
SESSION_TIMEOUT_IN_MINUTES = 30 # Session timeout in minutes
ANALYSIS_DAILY_LIMIT = 15 # Daily limit for analysis requests

# User Interface Configuration
# Primary: Blue (#007BFF) or Green (#22C55E) for medical trust
# Accent: Red (#EF4444) for blood analysis
# Neutrals: White & Dark Gray for a sleek UI
PRIMARY_COLOR = "#007BFF" # Blue
SECONDARY_COLOR = "#22C55E" # Green

# Other Configurations
from config.prompt import *
from config.sample import *