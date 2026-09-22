import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the banking customer support system."""
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "support_tickets.db")
    
    # System Configuration
    USE_LLM: bool = os.getenv("USE_LLM", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if cls.USE_LLM and not cls.OPENROUTER_API_KEY:
            print("Warning: USE_LLM is true but OPENROUTER_API_KEY is not set.")
            print("Falling back to rule-based classification.")
            cls.USE_LLM = False
            return False
        return True
    
    @classmethod
    def get_openai_client(cls):
        """Get configured OpenAI client for OpenRouter."""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in environment variables")
        
        from openai import OpenAI
        return OpenAI(
            api_key=cls.OPENROUTER_API_KEY,
            base_url=cls.OPENROUTER_BASE_URL
        )