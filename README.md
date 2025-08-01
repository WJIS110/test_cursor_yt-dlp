# yt-dlp Web Downloader

A simple web interface for downloading videos and audio from various platforms using yt-dlp.

## Features

- 🎥 Download videos from YouTube, SoundCloud, Vimeo, and other supported platforms
- 🎵 Extract audio-only downloads in MP3 format
- 📊 Get video information without downloading
- 📁 File management (list, download, delete)
- 🌐 RESTful API with OpenAPI documentation
- 🔧 Multiple quality options (720p, 480p, best quality)
- 🖥️ Local network access for home/office use
- ⚡ Built with FastAPI for high performance

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Open your browser and go to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

- `POST /api/v1/info` - Get video information
- `POST /api/v1/download` - Download video/audio
- `GET /api/v1/formats` - List available formats
- `GET /files/` - List downloaded files
- `GET /files/{filename}` - Download file
- `DELETE /files/{filename}` - Delete file

## Project Structure

```
├── app/
│   ├── main.py      # FastAPI application entry point
│   ├── config.py    # Configuration and settings
│   ├── models.py    # Pydantic data models
│   ├── services.py  # yt-dlp integration service
│   ├── routers.py   # API route handlers
│   └── __init__.py  # Package init
├── downloads/       # Downloaded files directory
├── requirements.txt # Project dependencies
└── README.md       # This file
```

## Development

This project is designed for learning purposes with a focus on:
- Clean code structure
- Easy-to-understand components
- Step-by-step implementation

More features will be added incrementally.