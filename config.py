import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Test Scenario Generator."""
    
    # Google Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # JIRA Configuration
    JIRA_URL = os.getenv("JIRA_URL")  # e.g., 'https://company.atlassian.net'
    JIRA_USERNAME = os.getenv("JIRA_USERNAME")  # JIRA username/email
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")  # JIRA API token
    
    # Confluence Configuration (legacy - keeping for compatibility)
    CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
    CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
    CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
    
    # Model Configuration
    MODEL_NAME = "gemini-2.5-pro"  # Google Gemini 2.5 Pro
    TEMPERATURE = 0.3
    
    # Token Configuration for Gemini 2.5 Pro
    # Context Window: 2M tokens, Max Output: ~65k tokens
    # Our data: PRD + Images + Excel + Prompts = ~25k+ tokens
    # Analysis outputs: JSON responses = ~10k+ tokens  
    MAX_TOKENS = 32768  # Increased to 32k tokens (was 4096) to handle large contexts and comprehensive analysis
    
    # Output Configuration
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        missing_vars = []
        
        if not cls.GOOGLE_API_KEY:
            missing_vars.append("GOOGLE_API_KEY")
        if not cls.CONFLUENCE_USERNAME:
            missing_vars.append("CONFLUENCE_USERNAME")
        if not cls.CONFLUENCE_API_TOKEN:
            missing_vars.append("CONFLUENCE_API_TOKEN")
            
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 