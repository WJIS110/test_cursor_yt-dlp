#!/usr/bin/env python3
"""
视频下载器服务器启动脚本
"""

import sys
import os

def main():
    print("🚀 启动视频下载器服务器...")
    
    try:
        # 检查依赖
        import fastapi
        import uvicorn
        import yt_dlp
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    try:
        # 导入主应用
        from main import app
        print("✅ 应用导入成功")
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        return
    
    try:
        # 启动服务器
        print("🌐 启动服务器...")
        print("📍 服务器地址: http://localhost:8000")
        print("📚 API 文档: http://localhost:8000/docs")
        print("🎥 Web 界面: http://localhost:8000/")
        print("⚠️  按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

if __name__ == "__main__":
    main()