import os

class Settings:
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "") # Used for session management
    REDIRECT_URI: str = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/google") # Default for development, adjust for production

    def __init__(self):
        if not self.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID environment variable not set.")
        if not self.GOOGLE_CLIENT_SECRET:
            raise ValueError("GOOGLE_CLIENT_SECRET environment variable not set.")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable not set.")

settings = Settings()