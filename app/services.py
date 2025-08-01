import yt_dlp
import os
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .config import settings
from .models import VideoInfo, VideoFormat, DownloadFormat, DownloadResponse

class YTDLPService:
    """Service class for handling yt-dlp operations"""
    
    def __init__(self):
        """Initialize the yt-dlp service with default options"""
        self.base_options = {
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': False,
            'no_warnings': False,
            # Add options to handle YouTube restrictions better
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web']
                }
            }
        }
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Extract video information without downloading
        
        Args:
            url: Video URL to extract info from
            
        Returns:
            VideoInfo object with video metadata
            
        Raises:
            Exception: If video info extraction fails
        """
        try:
            # Configure yt-dlp options for info extraction only
            ydl_opts = {
                **self.base_options,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading
                info = ydl.extract_info(url, download=False)
                
                # Parse available formats
                formats = []
                if info.get('formats'):
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                            formats.append(VideoFormat(
                                format_id=fmt.get('format_id', ''),
                                ext=fmt.get('ext', ''),
                                quality=fmt.get('quality'),
                                filesize=fmt.get('filesize'),
                                format_note=fmt.get('format_note')
                            ))
                
                # Return structured video info
                return VideoInfo(
                    title=info.get('title', 'Unknown Title'),
                    duration=info.get('duration'),
                    uploader=info.get('uploader'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    thumbnail=info.get('thumbnail'),
                    description=info.get('description'),
                    formats=formats[:10]  # Limit to first 10 formats to avoid overwhelming response
                )
                
        except Exception as e:
            raise Exception(f"Failed to extract video info: {str(e)}")
    
    def download_video(self, url: str, format_type: DownloadFormat) -> DownloadResponse:
        """
        Download video or audio based on specified format
        
        Args:
            url: Video URL to download
            format_type: Download format specification
            
        Returns:
            DownloadResponse with download result
        """
        try:
            # Ensure download directory exists
            settings.DOWNLOAD_DIR.mkdir(exist_ok=True)
            
            # Configure download options based on format
            ydl_opts = self._get_download_options(format_type)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get filename
                info = ydl.extract_info(url, download=False)
                
                # Generate filename
                filename = ydl.prepare_filename(info)
                file_path = Path(filename)
                
                # Download the video/audio
                ydl.download([url])
                
                # Check if file was created and get its size
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    return DownloadResponse(
                        success=True,
                        message="Download completed successfully",
                        filename=file_path.name,
                        file_size=file_size,
                        download_url=f"/files/{file_path.name}"
                    )
                else:
                    return DownloadResponse(
                        success=False,
                        message="Download failed - file not found after download"
                    )
                    
        except Exception as e:
            return DownloadResponse(
                success=False,
                message=f"Download failed: {str(e)}"
            )
    
    def _get_download_options(self, format_type: DownloadFormat) -> Dict[str, Any]:
        """
        Get yt-dlp options based on download format
        
        Args:
            format_type: Desired download format
            
        Returns:
            Dictionary of yt-dlp options
        """
        base_opts = {
            **self.base_options,
            'outtmpl': str(settings.DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'restrictfilenames': True,  # Avoid special characters in filename
        }
        
        if format_type == DownloadFormat.VIDEO_BEST:
            base_opts['format'] = 'best[height<=1080]'
        elif format_type == DownloadFormat.VIDEO_720P:
            base_opts['format'] = 'best[height<=720]'
        elif format_type == DownloadFormat.VIDEO_480P:
            base_opts['format'] = 'best[height<=480]'
        elif format_type == DownloadFormat.AUDIO_BEST:
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif format_type == DownloadFormat.AUDIO_MP3:
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': settings.AUDIO_QUALITY,
                }],
            })
        
        return base_opts
    
    def is_supported_url(self, url: str) -> bool:
        """
        Check if the URL is from a supported platform
        
        Args:
            url: URL to check
            
        Returns:
            True if supported, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return any(allowed_domain in domain for allowed_domain in settings.ALLOWED_DOMAINS)
        except:
            return False

# Create global service instance
ytdlp_service = YTDLPService()