from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from pathlib import Path as PathLib
import asyncio
from datetime import datetime

from api.models import (
    DownloadRequest, JobResponse, JobStatusResponse, 
    VideoInfo, FileInfo, JobStatus
)
from core.job_manager import JobManager
from api.websocket import websocket_manager
from config import DOWNLOAD_DIR, QUALITY_OPTIONS

# 创建路由器
router = APIRouter(prefix="/api", tags=["video_downloader"])

# 全局任务管理器实例
job_manager = None

def init_job_manager():
    """初始化任务管理器"""
    global job_manager
    if job_manager is None:
        # 创建异步回调包装器
        def sync_websocket_callback(job_id: str, job_status: JobStatusResponse):
            """同步回调包装器"""
            asyncio.create_task(websocket_manager.send_job_update(job_id, job_status))
        
        job_manager = JobManager(websocket_callback=sync_websocket_callback)
    return job_manager

@router.post("/download", response_model=JobResponse)
async def start_download(request: DownloadRequest):
    """
    开始下载任务
    
    - **url**: 视频URL
    - **format**: 格式选择器 (默认: "best")
    - **audio_only**: 是否仅下载音频 (默认: False)
    """
    manager = init_job_manager()
    
    try:
        # 验证URL（简单检查）
        if not request.url.strip():
            raise HTTPException(status_code=400, detail="URL不能为空")
        
        # 创建下载任务
        job_id = manager.create_job(
            url=request.url,
            format_selector=request.format,
            audio_only=request.audio_only
        )
        
        # 启动下载
        success = manager.start_download(job_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="启动下载失败")
        
        # 发送系统消息
        await websocket_manager.send_system_message(
            f"开始下载: {request.url}", "info"
        )
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.DOWNLOADING,
            message="下载已开始"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建下载任务失败: {str(e)}")

@router.get("/download/{job_id}", response_model=JobStatusResponse)
async def get_download_status(
    job_id: str = Path(..., description="任务ID")
):
    """
    获取下载任务状态
    
    - **job_id**: 任务ID
    """
    manager = init_job_manager()
    
    job_status = manager.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return job_status

@router.delete("/download/{job_id}")
async def cancel_download(
    job_id: str = Path(..., description="任务ID")
):
    """
    取消下载任务
    
    - **job_id**: 任务ID
    """
    manager = init_job_manager()
    
    success = manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法取消")
    
    await websocket_manager.send_system_message(
        f"任务已取消: {job_id}", "warning"
    )
    
    return {"message": "任务已取消", "job_id": job_id}

@router.get("/downloads", response_model=List[JobStatusResponse])
async def get_all_downloads(
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    status: Optional[JobStatus] = Query(None, description="按状态过滤")
):
    """
    获取所有下载任务
    
    - **limit**: 返回数量限制 (1-100)
    - **status**: 按状态过滤 (可选)
    """
    manager = init_job_manager()
    
    all_jobs = manager.get_all_jobs()
    
    # 按状态过滤
    if status:
        all_jobs = [job for job in all_jobs if job.status == status]
    
    # 限制返回数量
    return all_jobs[:limit]

@router.get("/info")
async def get_video_info(
    url: str = Query(..., description="视频URL")
):
    """
    获取视频信息（不下载）
    
    - **url**: 视频URL
    """
    manager = init_job_manager()
    
    try:
        info = manager.get_video_info(url)
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取视频信息失败: {str(e)}")

@router.get("/files", response_model=List[FileInfo])
async def list_downloaded_files():
    """
    列出已下载的文件
    """
    try:
        files = []
        download_path = PathLib(DOWNLOAD_DIR)
        
        if download_path.exists():
            for file_path in download_path.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(FileInfo(
                        filename=file_path.name,
                        filepath=str(file_path),
                        size=stat.st_size,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        download_url=f"/api/files/{file_path.name}/download"
                    ))
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x.created_at, reverse=True)
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.get("/files/{filename}/download")
async def download_file(
    filename: str = Path(..., description="文件名")
):
    """
    下载文件
    
    - **filename**: 文件名
    """
    file_path = PathLib(DOWNLOAD_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="不是有效的文件")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@router.delete("/files/{filename}")
async def delete_file(
    filename: str = Path(..., description="文件名")
):
    """
    删除文件
    
    - **filename**: 文件名
    """
    file_path = PathLib(DOWNLOAD_DIR) / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        file_path.unlink()
        
        await websocket_manager.send_system_message(
            f"文件已删除: {filename}", "info"
        )
        
        return {"message": f"文件已删除: {filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

@router.get("/formats")
async def get_supported_formats():
    """
    获取支持的格式选项
    """
    return {
        "formats": QUALITY_OPTIONS,
        "description": "支持的下载格式和质量选项"
    }

@router.get("/stats")
async def get_system_stats():
    """
    获取系统统计信息
    """
    manager = init_job_manager()
    
    # 统计各状态的任务数量
    all_jobs = manager.get_all_jobs()
    stats = {
        "total_jobs": len(all_jobs),
        "pending": len([j for j in all_jobs if j.status == JobStatus.PENDING]),
        "downloading": len([j for j in all_jobs if j.status == JobStatus.DOWNLOADING]),
        "completed": len([j for j in all_jobs if j.status == JobStatus.COMPLETED]),
        "failed": len([j for j in all_jobs if j.status == JobStatus.FAILED]),
        "cancelled": len([j for j in all_jobs if j.status == JobStatus.CANCELLED]),
    }
    
    # 文件统计
    try:
        download_path = PathLib(DOWNLOAD_DIR)
        total_files = 0
        total_size = 0
        
        if download_path.exists():
            for file_path in download_path.iterdir():
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
        
        stats.update({
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        })
    except Exception:
        stats.update({
            "total_files": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0,
        })
    
    # WebSocket 连接统计
    stats.update({
        "active_connections": websocket_manager.get_connection_count(),
        "connections": websocket_manager.get_connection_info()
    })
    
    return stats

@router.post("/cleanup")
async def cleanup_jobs():
    """
    清理旧任务（保留最近100个）
    """
    manager = init_job_manager()
    
    before_count = len(manager.get_all_jobs())
    manager.cleanup_old_jobs(max_jobs=100)
    after_count = len(manager.get_all_jobs())
    
    cleaned_count = before_count - after_count
    
    if cleaned_count > 0:
        await websocket_manager.send_system_message(
            f"已清理 {cleaned_count} 个旧任务", "info"
        )
    
    return {
        "message": f"清理完成，删除了 {cleaned_count} 个旧任务",
        "before_count": before_count,
        "after_count": after_count
    }