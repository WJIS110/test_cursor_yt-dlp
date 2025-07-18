import os
from pathlib import Path

# 基本配置
APP_NAME = "Video Downloader"
VERSION = "1.0.0"
HOST = "0.0.0.0"  # 监听所有网络接口，允许局域网访问
PORT = 8000

# 文件路径配置
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
STATIC_DIR = BASE_DIR / "static"
DATABASE_PATH = BASE_DIR / "downloads.db"

# 确保下载目录存在
DOWNLOAD_DIR.mkdir(exist_ok=True)

# yt-dlp 默认配置
YT_DLP_OPTIONS = {
    'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
    'format': 'best',
    'writesubtitles': False,
    'writeautomaticsub': False,
    'ignoreerrors': True,
}

# 支持的格式选项
QUALITY_OPTIONS = [
    {'value': 'best', 'label': '最佳质量'},
    {'value': 'worst', 'label': '最低质量'},
    {'value': 'bestvideo+bestaudio', 'label': '最佳视频+音频'},
    {'value': 'bestaudio', 'label': '仅音频（最佳）'},
    {'value': 'mp4', 'label': 'MP4格式'},
    {'value': 'webm', 'label': 'WebM格式'},
]

# WebSocket配置
MAX_CONNECTIONS = 10