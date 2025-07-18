import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable
from api.models import JobStatus, JobStatusResponse
from core.downloader import VideoDownloader

class JobManager:
    """任务管理器 - 内存中跟踪下载任务"""
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        """
        初始化任务管理器
        
        Args:
            websocket_callback: WebSocket回调函数，用于发送实时更新
        """
        self.jobs: Dict[str, Dict] = {}  # job_id -> job_data
        self.lock = threading.Lock()
        self.websocket_callback = websocket_callback
        self.downloader = VideoDownloader(progress_callback=self._on_progress_update)
    
    def create_job(self, url: str, format_selector: str = "best", 
                   audio_only: bool = False) -> str:
        """
        创建新的下载任务
        
        Args:
            url: 视频URL
            format_selector: 格式选择器
            audio_only: 是否仅下载音频
            
        Returns:
            任务ID
        """
        job_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        job_data = {
            'job_id': job_id,
            'url': url,
            'format': format_selector,
            'audio_only': audio_only,
            'status': JobStatus.PENDING,
            'progress': 0.0,
            'speed': None,
            'eta': None,
            'title': None,
            'filename': None,
            'error_message': None,
            'created_at': current_time,
            'updated_at': current_time,
            'thread': None
        }
        
        with self.lock:
            self.jobs[job_id] = job_data
        
        return job_id
    
    def start_download(self, job_id: str) -> bool:
        """
        开始下载任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否成功启动
        """
        with self.lock:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            if job['status'] != JobStatus.PENDING:
                return False
            
            # 更新状态为下载中
            job['status'] = JobStatus.DOWNLOADING
            job['updated_at'] = datetime.now()
        
        # 在新线程中开始下载
        thread = threading.Thread(
            target=self._download_worker,
            args=(job_id,),
            daemon=True
        )
        
        with self.lock:
            self.jobs[job_id]['thread'] = thread
        
        thread.start()
        return True
    
    def _download_worker(self, job_id: str):
        """下载工作线程"""
        try:
            with self.lock:
                job = self.jobs[job_id]
                url = job['url']
                format_selector = job['format']
                audio_only = job['audio_only']
            
            # 执行下载
            result = self.downloader.download(
                job_id=job_id,
                url=url,
                format_selector=format_selector,
                audio_only=audio_only
            )
            
            # 更新任务状态
            with self.lock:
                if job_id in self.jobs:
                    job = self.jobs[job_id]
                    
                    if result['status'] == 'completed':
                        job['status'] = JobStatus.COMPLETED
                        job['progress'] = 100.0
                        job['title'] = result.get('title')
                        job['filename'] = result.get('filename')
                    elif result['status'] == 'cancelled':
                        job['status'] = JobStatus.CANCELLED
                    else:
                        job['status'] = JobStatus.FAILED
                        job['error_message'] = result.get('error', '下载失败')
                    
                    job['updated_at'] = datetime.now()
            
            # 发送最终状态更新
            self._send_websocket_update(job_id)
            
        except Exception as e:
            # 处理异常
            with self.lock:
                if job_id in self.jobs:
                    job = self.jobs[job_id]
                    job['status'] = JobStatus.FAILED
                    job['error_message'] = str(e)
                    job['updated_at'] = datetime.now()
            
            self._send_websocket_update(job_id)
    
    def _on_progress_update(self, job_id: str, progress_data: Dict):
        """处理进度更新"""
        with self.lock:
            if job_id not in self.jobs:
                return
            
            job = self.jobs[job_id]
            job['progress'] = progress_data.get('progress', 0.0)
            job['speed'] = progress_data.get('speed')
            job['eta'] = progress_data.get('eta')
            
            if progress_data.get('filename'):
                job['filename'] = progress_data['filename']
            
            job['updated_at'] = datetime.now()
        
        # 发送WebSocket更新
        self._send_websocket_update(job_id)
    
    def _send_websocket_update(self, job_id: str):
        """发送WebSocket更新"""
        if not self.websocket_callback:
            return
        
        job_status = self.get_job_status(job_id)
        if job_status:
            self.websocket_callback(job_id, job_status)
    
    def get_job_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """
        获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务状态响应
        """
        with self.lock:
            if job_id not in self.jobs:
                return None
            
            job = self.jobs[job_id]
            return JobStatusResponse(
                job_id=job_id,
                status=job['status'],
                progress=job['progress'],
                speed=job['speed'],
                eta=job['eta'],
                title=job['title'],
                filename=job['filename'],
                error_message=job['error_message'],
                created_at=job['created_at'],
                updated_at=job['updated_at']
            )
    
    def cancel_job(self, job_id: str) -> bool:
        """
        取消任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否成功取消
        """
        with self.lock:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            if job['status'] not in [JobStatus.PENDING, JobStatus.DOWNLOADING]:
                return False
            
            job['status'] = JobStatus.CANCELLED
            job['updated_at'] = datetime.now()
        
        # 通知下载器取消
        self.downloader.cancel_download(job_id)
        
        # 发送更新
        self._send_websocket_update(job_id)
        return True
    
    def get_all_jobs(self) -> List[JobStatusResponse]:
        """获取所有任务状态"""
        with self.lock:
            result = []
            for job_id in self.jobs:
                job_status = self.get_job_status(job_id)
                if job_status:
                    result.append(job_status)
            
            # 按创建时间倒序排列
            result.sort(key=lambda x: x.created_at, reverse=True)
            return result
    
    def cleanup_old_jobs(self, max_jobs: int = 100):
        """清理旧任务，保持内存使用合理"""
        with self.lock:
            if len(self.jobs) <= max_jobs:
                return
            
            # 获取已完成的任务，按时间排序
            completed_jobs = [
                (job_id, job['updated_at']) 
                for job_id, job in self.jobs.items() 
                if job['status'] in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            ]
            
            completed_jobs.sort(key=lambda x: x[1])
            
            # 删除最旧的任务
            jobs_to_remove = len(self.jobs) - max_jobs
            for i in range(min(jobs_to_remove, len(completed_jobs))):
                job_id = completed_jobs[i][0]
                del self.jobs[job_id]
    
    def get_video_info(self, url: str) -> Dict:
        """获取视频信息"""
        return self.downloader.get_video_info(url)