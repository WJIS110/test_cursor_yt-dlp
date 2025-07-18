from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """下载任务状态"""
    PENDING = "pending"      # 等待中
    DOWNLOADING = "downloading"  # 下载中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消

class DownloadRequest(BaseModel):
    """下载请求模型"""
    url: str
    format: str = "best"
    audio_only: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "best",
                "audio_only": False
            }
        }

class JobResponse(BaseModel):
    """任务响应模型"""
    job_id: str
    status: JobStatus
    message: str = ""
    
class JobStatusResponse(BaseModel):
    """任务状态响应模型"""
    job_id: str
    status: JobStatus
    progress: float = 0.0  # 0-100
    speed: Optional[str] = None
    eta: Optional[str] = None
    title: Optional[str] = None
    filename: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class VideoInfo(BaseModel):
    """视频信息模型"""
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    available_formats: List[Dict[str, Any]] = []

class FileInfo(BaseModel):
    """文件信息模型"""
    filename: str
    filepath: str
    size: int
    created_at: datetime
    download_url: str

class ProgressUpdate(BaseModel):
    """进度更新模型（WebSocket）"""
    job_id: str
    progress: float
    speed: Optional[str] = None
    eta: Optional[str] = None
    status: JobStatus
    filename: Optional[str] = None