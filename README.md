# Video Downloader

一個使用 FastAPI 和 yt-dlp 的影片下載工具，支援網頁界面和 API 調用。

## 功能特色

- 🎬 下載 YouTube 等平台的影片和音訊
- 🌐 簡潔的 Web 介面
- 🔗 RESTful API，可被其他程式調用
- 📱 響應式設計，支援手機瀏覽
- 🎯 適合初學者學習的程式碼結構

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動服務

```bash
python run.py
```

### 3. 開始使用

- **網頁界面**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **區域網路訪問**: http://你的IP:8000

## API 使用範例

### 下載影片

```python
import requests

response = requests.post("http://localhost:8000/download", 
                        json={"url": "https://www.youtube.com/watch?v=example", 
                              "format_type": "mp4"})
print(response.json())
```

### 獲取影片資訊

```python
response = requests.post("http://localhost:8000/info", 
                        json={"url": "https://www.youtube.com/watch?v=example"})
print(response.json())
```

### 列出已下載檔案

```python
response = requests.get("http://localhost:8000/files")
print(response.json())
```

## 專案結構

```
video_downloader/
├── app/
│   ├── __init__.py          # 套件初始化
│   ├── main.py              # FastAPI 主應用
│   ├── downloader.py        # yt-dlp 下載功能
│   └── models.py            # 資料模型
├── static/
│   ├── index.html           # 主頁面
│   ├── style.css            # 樣式檔案
│   └── script.js            # JavaScript 邏輯
├── downloads/               # 下載檔案存放
├── requirements.txt         # Python 依賴
└── run.py                   # 啟動腳本
```

## 作為 Python 模組使用

```python
from app.downloader import VideoDownloader

# 建立下載器實例
downloader = VideoDownloader(output_dir="my_downloads")

# 下載影片
result = downloader.download("https://www.youtube.com/watch?v=example", "mp4")
print(result)

# 獲取影片資訊
info = downloader.get_video_info("https://www.youtube.com/watch?v=example")
print(info)
```

## 注意事項

- 本工具僅供個人學習使用
- 請遵守相關平台的使用條款和版權法規
- 下載的檔案會存放在 `downloads/` 目錄
- 服務預設運行在 8000 埠，可在區域網路內訪問

## 系統需求

- Python 3.8+
- 網路連線
- FFmpeg（下載 MP3 格式時需要）