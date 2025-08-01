"""
Video Downloader FastAPI 應用程式
提供 Web 介面和 API 來下載影片
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict

from .downloader import VideoDownloader
from .models import DownloadRequest, DownloadResponse, VideoInfoRequest, VideoInfoResponse

# 建立 FastAPI 應用實例
app = FastAPI(
    title="Video Downloader",
    description="使用 yt-dlp 下載影片和音訊的 Web 應用程式",
    version="1.0.0"
)

# 建立下載器實例
downloader = VideoDownloader()

# 掛載靜態檔案目錄
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    主頁面路由
    返回 HTML 檔案
    """
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>主頁面檔案未找到</h1><p>請確保 static/index.html 存在</p>",
            status_code=404
        )


@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest):
    """
    下載影片 API
    
    Args:
        request: 包含 URL 和格式的下載請求
        
    Returns:
        下載結果
    """
    try:
        # 將 URL 轉換為字串（Pydantic HttpUrl 類型）
        url_str = str(request.url)
        
        # 執行下載
        result = downloader.download(url_str, request.format_type)
        
        return DownloadResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"下載過程中發生錯誤: {str(e)}"
        )


@app.post("/info", response_model=VideoInfoResponse)
async def get_video_info(request: VideoInfoRequest):
    """
    獲取影片資訊 API（不下載）
    
    Args:
        request: 包含 URL 的請求
        
    Returns:
        影片資訊
    """
    try:
        url_str = str(request.url)
        result = downloader.get_video_info(url_str)
        
        return VideoInfoResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取影片資訊時發生錯誤: {str(e)}"
        )


@app.get("/files")
async def list_files():
    """
    列出已下載的檔案
    
    Returns:
        檔案列表
    """
    try:
        files = []
        download_dir = "downloads"
        
        if os.path.exists(download_dir):
            for filename in os.listdir(download_dir):
                file_path = os.path.join(download_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "name": filename,
                        "size": file_size,
                        "download_url": f"/downloads/{filename}"
                    })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"讀取檔案列表時發生錯誤: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    健康檢查端點
    
    Returns:
        系統狀態
    """
    return {
        "status": "healthy",
        "message": "Video Downloader 運行正常"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)