# yt-dlp Web Downloader

A simple web interface for downloading videos and audio from various platforms using yt-dlp.

## Features

- Download videos from YouTube, SoundCloud, Vimeo, and other supported platforms
- Extract audio-only downloads
- Simple web interface
- Local network access
- Built with FastAPI for easy integration

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

## Project Structure

```
├── app/
│   ├── main.py      # FastAPI application
│   ├── config.py    # Configuration settings
│   └── __init__.py  # Package init
├── requirements.txt # Dependencies
└── README.md       # This file
```

## Development

This project is designed for learning purposes with a focus on:
- Clean code structure
- Easy-to-understand components
- Step-by-step implementation

More features will be added incrementally.