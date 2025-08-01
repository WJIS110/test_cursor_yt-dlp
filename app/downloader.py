"""
影片下載器模組
使用 yt-dlp 下載影片和音訊
"""
import os
import yt_dlp
from typing import Dict, Any


class VideoDownloader:
    """簡單的影片下載器類別"""
    
    def __init__(self, output_dir: str = "downloads"):
        """
        初始化下載器
        
        Args:
            output_dir: 下載檔案的存放目錄
        """
        self.output_dir = output_dir
        # 確保下載目錄存在
        os.makedirs(output_dir, exist_ok=True)
    
    def download(self, url: str, format_type: str = "best") -> Dict[str, Any]:
        """
        下載影片或音訊
        
        Args:
            url: 影片連結
            format_type: 下載格式 ("best", "mp4", "mp3")
            
        Returns:
            下載結果字典
        """
        try:
            # 設定 yt-dlp 選項
            ydl_opts = {
                'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            }
            
            # 根據格式類型調整設定
            if format_type == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif format_type == "mp4":
                ydl_opts['format'] = 'best[ext=mp4]/mp4/best'
            
            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先獲取影片資訊
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # 執行下載
                ydl.download([url])
                
                return {
                    "status": "success",
                    "message": "下載完成",
                    "title": title,
                    "url": url
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"下載失敗: {str(e)}",
                "url": url
            }
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        獲取影片資訊（不下載）
        
        Args:
            url: 影片連結
            
        Returns:
            影片資訊字典
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "status": "success",
                    "title": info.get('title', 'Unknown'),
                    "duration": info.get('duration', 0),
                    "uploader": info.get('uploader', 'Unknown'),
                    "view_count": info.get('view_count', 0),
                    "upload_date": info.get('upload_date', ''),
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"無法獲取影片資訊: {str(e)}"
            }