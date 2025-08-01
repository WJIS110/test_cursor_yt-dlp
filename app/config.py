import os
from pathlib import Path

class Settings:
    """Application settings and configuration"""
    
    # Application settings
    APP_NAME: str = "yt-dlp Web Downloader"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"  # Allow connections from local network
    PORT: int = 8000
    
    # Download settings
    DOWNLOAD_DIR: Path = Path("downloads")
    MAX_FILE_SIZE: int = 1024 * 1024 * 1024  # 1GB limit
    ALLOWED_DOMAINS: list = [
        "youtube.com", "youtu.be", "soundcloud.com", 
        "vimeo.com", "dailymotion.com", "twitch.tv"
    ]
    
    # yt-dlp settings
    YTDLP_FORMAT: str = "best[height<=720]"  # Default to 720p max
    AUDIO_FORMAT: str = "mp3"
    AUDIO_QUALITY: str = "192"  # kbps
    
    def __init__(self):
        """Initialize settings and create download directory"""
        # Create download directory if it doesn't exist
        self.DOWNLOAD_DIR.mkdir(exist_ok=True)
        
        # Allow environment variable overrides
        if os.getenv("DOWNLOAD_DIR"):
            self.DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR"))
            self.DOWNLOAD_DIR.mkdir(exist_ok=True)
            
        if os.getenv("PORT"):
            self.PORT = int(os.getenv("PORT"))

# Create global settings instance
settings = Settings()