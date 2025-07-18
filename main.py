from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from pathlib import Path

from api.routes import router as api_router
from api.websocket import websocket_endpoint
from config import APP_NAME, VERSION, HOST, PORT, STATIC_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="基于 FastAPI 和 yt-dlp 的视频下载器",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 包含 API 路由
app.include_router(api_router)

# WebSocket 端点
@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    """WebSocket 连接处理"""
    await websocket_endpoint(websocket)

# 确保静态文件目录存在
STATIC_DIR.mkdir(exist_ok=True)

# 挂载静态文件服务
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    首页 - 返回主界面
    """
    index_file = STATIC_DIR / "index.html"
    
    # 如果 index.html 不存在，返回简单的欢迎页面
    if not index_file.exists():
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>视频下载器</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                h1 {
                    margin: 0 0 20px 0;
                    font-size: 2.5em;
                }
                .subtitle {
                    font-size: 1.2em;
                    margin-bottom: 40px;
                    opacity: 0.9;
                }
                .links {
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                .link {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 15px 25px;
                    border-radius: 10px;
                    text-decoration: none;
                    color: white;
                    transition: all 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                .link:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: translateY(-2px);
                }
                .status {
                    margin-top: 40px;
                    padding: 20px;
                    background: rgba(0, 255, 0, 0.2);
                    border-radius: 10px;
                    border: 1px solid rgba(0, 255, 0, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎥 视频下载器</h1>
                <p class="subtitle">基于 FastAPI 和 yt-dlp 的在线视频下载工具</p>
                
                <div class="links">
                    <a href="/docs" class="link">📚 API 文档</a>
                    <a href="/redoc" class="link">📖 ReDoc 文档</a>
                    <a href="/api/stats" class="link">📊 系统状态</a>
                    <a href="/api/files" class="link">📁 文件列表</a>
                </div>
                
                <div class="status">
                    <h3>✅ 服务运行正常</h3>
                    <p>前端界面正在开发中...<br>
                    您可以直接使用 API 端点进行下载操作。</p>
                </div>
                
                <div style="margin-top: 40px; font-size: 0.9em; opacity: 0.7;">
                    <p>📡 WebSocket: ws://localhost:8000/ws</p>
                    <p>🔗 API 基础路径: /api</p>
                </div>
            </div>
        </body>
        </html>
        """)
    
    # 返回静态文件
    with open(index_file, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": VERSION,
        "message": "视频下载器运行正常"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info(f"🚀 {APP_NAME} v{VERSION} 启动中...")
    logger.info(f"📡 服务地址: http://{HOST}:{PORT}")
    logger.info(f"📚 API 文档: http://{HOST}:{PORT}/docs")
    logger.info(f"🔌 WebSocket: ws://{HOST}:{PORT}/ws")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("🛑 视频下载器正在关闭...")

if __name__ == "__main__":
    import uvicorn
    
    # 运行应用
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,  # 开发模式，生产环境应设为 False
        log_level="info"
    )