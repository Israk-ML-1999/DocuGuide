import os
from dotenv import load_dotenv
            
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            cls._instance.model_name = os.getenv("MODEL", "claude-sonnet-4-20250514")

        return cls._instance