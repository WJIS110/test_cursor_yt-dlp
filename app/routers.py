from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
import os

from .models import (
    VideoInfoRequest, VideoInfo, DownloadRequest, 
    DownloadResponse, ErrorResponse, DownloadFormat
)
from .services import ytdlp_service
from .config import settings

# Create router for video operations
video_router = APIRouter(prefix="/api/v1", tags=["Video Operations"])

@video_router.post("/info", response_model=VideoInfo)
async def get_video_info(request: VideoInfoRequest):
    """
    Get video information without downloading
    
    This endpoint extracts metadata from a video URL including:
    - Title, duration, uploader
    - Available formats and quality options
    - Thumbnail and description
    """
    try:
        # Validate URL is from supported platform
        if not ytdlp_service.is_supported_url(str(request.url)):
            raise HTTPException(
                status_code=400, 
                detail="URL is not from a supported platform"
            )
        
        # Extract video information
        video_info = ytdlp_service.get_video_info(str(request.url))
        return video_info
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@video_router.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest):
    """
    Download video or audio in specified format
    
    Supported formats:
    - video_best: Best quality video (up to 1080p)
    - video_720p: 720p video quality
    - video_480p: 480p video quality  
    - audio_best: Best quality audio
    - audio_mp3: MP3 audio format
    """
    try:
        # Validate URL is from supported platform
        if not ytdlp_service.is_supported_url(str(request.url)):
            raise HTTPException(
                status_code=400,
                detail="URL is not from a supported platform"
            )
        
        # Download the video/audio
        result = ytdlp_service.download_video(str(request.url), request.format)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@video_router.get("/formats")
async def get_available_formats():
    """
    Get list of available download formats
    """
    return {
        "formats": [
            {
                "id": "video_best",
                "name": "Best Video Quality",
                "description": "Best available video quality (up to 1080p)"
            },
            {
                "id": "video_720p", 
                "name": "720p Video",
                "description": "720p video quality"
            },
            {
                "id": "video_480p",
                "name": "480p Video", 
                "description": "480p video quality"
            },
            {
                "id": "audio_best",
                "name": "Best Audio Quality",
                "description": "Best available audio quality"
            },
            {
                "id": "audio_mp3",
                "name": "MP3 Audio",
                "description": "MP3 audio format (192kbps)"
            }
        ]
    }

# Create router for file operations
files_router = APIRouter(prefix="/files", tags=["File Operations"])

@files_router.get("/{filename}")
async def get_file(filename: str):
    """
    Serve downloaded files
    
    Returns the requested file for download
    """
    try:
        file_path = settings.DOWNLOAD_DIR / filename
        
        # Security check: ensure file is within download directory
        if not file_path.resolve().is_relative_to(settings.DOWNLOAD_DIR.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file for download
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@files_router.get("/")
async def list_files():
    """
    List all downloaded files
    """
    try:
        files = []
        if settings.DOWNLOAD_DIR.exists():
            for file_path in settings.DOWNLOAD_DIR.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created": stat.st_ctime,
                        "download_url": f"/files/{file_path.name}"
                    })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@files_router.delete("/{filename}")
async def delete_file(filename: str):
    """
    Delete a downloaded file
    """
    try:
        file_path = settings.DOWNLOAD_DIR / filename
        
        # Security check: ensure file is within download directory
        if not file_path.resolve().is_relative_to(settings.DOWNLOAD_DIR.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        file_path.unlink()
        
        return {"message": f"File {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")