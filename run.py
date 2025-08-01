"""
Video Downloader 啟動腳本
"""
import uvicorn

if __name__ == "__main__":
    print("=== Video Downloader 啟動中 ===")
    print("本地訪問: http://localhost:8000")
    print("API 文檔: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服務")
    print("=====================================")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",    # 允許區域網路訪問
        port=8000,
        reload=True,       # 開發模式下自動重載
        log_level="info"
    )