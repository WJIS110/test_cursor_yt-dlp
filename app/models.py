"""
資料模型定義
使用 Pydantic 定義 API 的資料結構
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional


class DownloadRequest(BaseModel):
    """下載請求模型"""
    url: HttpUrl
    format_type: Optional[str] = "best"
    
    class Config:
        # 提供範例資料
        schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format_type": "mp4"
            }
        }


class DownloadResponse(BaseModel):
    """下載回應模型"""
    status: str
    message: str
    title: Optional[str] = None
    url: Optional[str] = None


class VideoInfoRequest(BaseModel):
    """影片資訊請求模型"""
    url: HttpUrl


class VideoInfoResponse(BaseModel):
    """影片資訊回應模型"""
    status: str
    title: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    message: Optional[str] = None  # 錯誤訊息用