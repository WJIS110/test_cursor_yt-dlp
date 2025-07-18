import yt_dlp
from typing import Dict, Any, Callable, Optional
from pathlib import Path
import threading
from config import YT_DLP_OPTIONS, DOWNLOAD_DIR

class VideoDownloader:
    """视频下载器类 - 封装 yt-dlp 功能"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化下载器
        
        Args:
            progress_callback: 进度回调函数，接收 (job_id, progress_info) 参数
        """
        self.progress_callback = progress_callback
        self._cancel_events = {}  # job_id -> threading.Event
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取视频信息，不下载
        
        Args:
            url: 视频URL
            
        Returns:
            视频信息字典
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 整理返回的信息
                return {
                    'title': info.get('title', '未知标题'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count'),
                    'available_formats': self._extract_formats(info.get('formats', []))
                }
        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")
    
    def _extract_formats(self, formats: list) -> list:
        """提取并整理可用格式"""
        result = []
        seen_formats = set()
        
        for fmt in formats:
            if not fmt.get('format_id'):
                continue
                
            format_info = {
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext', ''),
                'resolution': fmt.get('resolution', '未知'),
                'filesize': fmt.get('filesize'),
                'vcodec': fmt.get('vcodec', ''),
                'acodec': fmt.get('acodec', ''),
            }
            
            # 避免重复格式
            format_key = f"{format_info['format_id']}_{format_info['ext']}"
            if format_key not in seen_formats:
                seen_formats.add(format_key)
                result.append(format_info)
        
        return result[:10]  # 限制返回数量
    
    def download(self, job_id: str, url: str, format_selector: str = "best", 
                 audio_only: bool = False) -> Dict[str, Any]:
        """
        下载视频
        
        Args:
            job_id: 任务ID
            url: 视频URL
            format_selector: 格式选择器
            audio_only: 是否仅下载音频
            
        Returns:
            下载结果字典
        """
        # 创建取消事件
        cancel_event = threading.Event()
        self._cancel_events[job_id] = cancel_event
        
        # 准备 yt-dlp 选项
        ydl_opts = YT_DLP_OPTIONS.copy()
        ydl_opts['format'] = format_selector
        
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['outtmpl'] = str(DOWNLOAD_DIR / '%(title)s.%(ext)s')
        
        # 添加进度钩子
        ydl_opts['progress_hooks'] = [lambda d: self._progress_hook(job_id, d)]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 检查是否被取消
                if cancel_event.is_set():
                    return {'status': 'cancelled', 'message': '下载已取消'}
                
                # 开始下载
                info = ydl.extract_info(url, download=True)
                
                # 获取下载的文件路径
                filename = ydl.prepare_filename(info)
                file_path = Path(filename)
                
                return {
                    'status': 'completed',
                    'title': info.get('title', '未知标题'),
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size': file_path.stat().st_size if file_path.exists() else 0
                }
                
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
        finally:
            # 清理取消事件
            self._cancel_events.pop(job_id, None)
    
    def _progress_hook(self, job_id: str, progress_info: Dict[str, Any]):
        """yt-dlp 进度回调"""
        if not self.progress_callback:
            return
        
        # 检查是否被取消
        if job_id in self._cancel_events and self._cancel_events[job_id].is_set():
            return
        
        status = progress_info.get('status')
        
        if status == 'downloading':
            # 计算下载进度
            downloaded = progress_info.get('downloaded_bytes', 0)
            total = progress_info.get('total_bytes') or progress_info.get('total_bytes_estimate', 0)
            
            progress_percent = 0
            if total > 0:
                progress_percent = (downloaded / total) * 100
            
            # 整理进度信息
            progress_data = {
                'progress': progress_percent,
                'speed': progress_info.get('_speed_str', ''),
                'eta': progress_info.get('_eta_str', ''),
                'filename': progress_info.get('filename', ''),
                'status': 'downloading'
            }
            
            self.progress_callback(job_id, progress_data)
        
        elif status == 'finished':
            # 下载完成
            progress_data = {
                'progress': 100.0,
                'filename': progress_info.get('filename', ''),
                'status': 'completed'
            }
            self.progress_callback(job_id, progress_data)
    
    def cancel_download(self, job_id: str):
        """取消下载"""
        if job_id in self._cancel_events:
            self._cancel_events[job_id].set()