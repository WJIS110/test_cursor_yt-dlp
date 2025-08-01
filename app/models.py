from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class DownloadFormat(str, Enum):
    """Available download formats"""
    VIDEO_BEST = "video_best"
    VIDEO_720P = "video_720p"
    VIDEO_480P = "video_480p"
    AUDIO_BEST = "audio_best"
    AUDIO_MP3 = "audio_mp3"

class VideoInfoRequest(BaseModel):
    """Request model for getting video information"""
    url: HttpUrl = Field(..., description="Video URL to get information for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }

class VideoFormat(BaseModel):
    """Video format information"""
    format_id: str
    ext: str
    quality: Optional[str] = None
    filesize: Optional[int] = None
    format_note: Optional[str] = None

class VideoInfo(BaseModel):
    """Video information response"""
    title: str
    duration: Optional[int] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    formats: List[VideoFormat] = []
    
class DownloadRequest(BaseModel):
    """Request model for downloading videos"""
    url: HttpUrl = Field(..., description="Video URL to download")
    format: DownloadFormat = Field(default=DownloadFormat.VIDEO_BEST, description="Download format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "video_720p"
            }
        }

class DownloadResponse(BaseModel):
    """Response model for download operations"""
    success: bool
    message: str
    filename: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[str] = None