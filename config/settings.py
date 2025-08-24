"""Configuration settings for IntelliDoc Research Pro"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Settings
    COMET_API_KEY = os.getenv('COMET_API_KEY', '')
    COMET_BASE_URL = "https://api.cometapi.com/v1"

    # Legacy AI/ML API settings (kept for compatibility)
    AIMLAPI_KEY = os.getenv('AIMLAPI_KEY', '')
    AIMLAPI_BASE_URL = "https://api.aimlapi.com/v1"

    # GPT-5 Models
    GPT5_MODEL = os.getenv('GPT5_MODEL', 'gpt-5-nano')
    GPT5_MINI_MODEL = os.getenv('GPT5_MINI_MODEL', 'gpt-5-mini')
    GPT5_NANO_MODEL = os.getenv('GPT5_NANO_MODEL', 'gpt-5-nano')

    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'IntelliDoc Research Pro')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
    MAX_TOKENS_PER_REQUEST = int(os.getenv('MAX_TOKENS_PER_REQUEST', 4000))

    # File Processing
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))
    ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'pdf,txt,docx,jpg,png').split(',')

    # Export Settings
    EXPORT_PATH = os.getenv('EXPORT_PATH', './exports')

    # Research Settings
    CITATION_STYLES = ['APA 7th', 'MLA 9th', 'Chicago 17th', 'IEEE', 'Harvard']
    ANALYSIS_DEPTHS = ['Quick', 'Standard', 'Comprehensive', 'Exhaustive']
    REASONING_LEVELS = ['low', 'medium', 'high']

    # UI Settings
    PAGE_ICON = "🔬"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.COMET_API_KEY:
            raise ValueError("COMET_API_KEY is required. Please set it in your .env file")
        return True