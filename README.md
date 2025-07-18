# 视频下载器 (Video Downloader)

一个基于 FastAPI 和 yt-dlp 的简单视频/音频下载工具，专为本地局域网使用设计。

## 功能特性

- 🎥 **视频下载** - 支持多种视频平台（YouTube、Bilibili等）
- 🎵 **音频提取** - 仅下载音频文件
- 📊 **实时进度** - WebSocket 实时显示下载进度
- 🔄 **多种格式** - 支持不同质量和格式选择
- 🌐 **API 优先** - 可以被其他脚本调用
- 📱 **响应式界面** - 现代化的 Web 界面
- 🚀 **无需数据库** - 轻量级内存存储
- 🔧 **易于扩展** - 模块化设计

## 技术栈

- **后端**: FastAPI + yt-dlp + Python 3.8+
- **前端**: 原生 HTML5 + CSS3 + JavaScript (ES6+)
- **实时通信**: WebSocket
- **下载引擎**: yt-dlp (无 subprocess 调用)

## 项目结构

```
video-downloader/
├── main.py                 # FastAPI 应用入口
├── config.py               # 配置文件
├── requirements.txt        # Python 依赖
├── api/                    # API 相关
│   ├── models.py          # Pydantic 数据模型
│   ├── routes.py          # API 路由
│   └── websocket.py       # WebSocket 处理
├── core/                   # 核心功能
│   ├── downloader.py      # yt-dlp 封装
│   ├── job_manager.py     # 任务管理
│   └── database.py        # 数据存储
├── static/                 # 前端文件
│   ├── index.html
│   ├── css/style.css
│   └── js/
└── downloads/              # 下载文件存储
```

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
# 开发模式
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 访问界面

- **Web 界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **局域网访问**: http://[你的IP]:8000

## API 使用示例

### 开始下载

```python
import requests

# 开始下载
response = requests.post("http://localhost:8000/api/download", 
                        json={
                            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "format": "best",
                            "audio_only": False
                        })
job_id = response.json()["job_id"]
print(f"任务ID: {job_id}")
```

### 查询状态

```python
# 查询下载状态
status = requests.get(f"http://localhost:8000/api/download/{job_id}")
print(status.json())
```

### 获取视频信息

```python
# 获取视频信息（不下载）
info = requests.get("http://localhost:8000/api/info/https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(info.json())
```

## API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/download` | 开始下载任务 |
| GET | `/api/download/{job_id}` | 获取任务状态 |
| DELETE | `/api/download/{job_id}` | 取消任务 |
| GET | `/api/downloads` | 获取所有任务 |
| GET | `/api/files` | 列出下载的文件 |
| DELETE | `/api/files/{filename}` | 删除文件 |
| GET | `/api/info/{url}` | 获取视频信息 |
| WebSocket | `/ws` | 实时进度更新 |

## 配置说明

编辑 `config.py` 来自定义设置：

```python
# 服务器配置
HOST = "0.0.0.0"  # 监听地址
PORT = 8000       # 端口

# 下载配置
DOWNLOAD_DIR = "downloads"  # 下载目录
YT_DLP_OPTIONS = {          # yt-dlp 选项
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s'
}
```

## 特色设计

### 1. 无 subprocess 调用
直接使用 yt-dlp 的 Python API，避免子进程开销和安全问题。

### 2. 内存优先存储
活动任务存储在内存中，确保快速访问，只有完成的任务才会持久化。

### 3. 线程安全
使用线程锁确保并发安全，支持多用户同时使用。

### 4. 实时更新
WebSocket 提供实时进度更新，无需轮询。

### 5. 模块化设计
核心下载逻辑可以独立使用，方便集成到其他项目。

## 支持的平台

通过 yt-dlp 支持 1000+ 视频平台，包括但不限于：

- YouTube
- Bilibili
- Twitter
- TikTok
- Vimeo
- Twitch
- 更多平台...

## 开发说明

这个项目专为学习目的设计，代码结构清晰，注释详细，适合初级工程师理解和扩展。

### 扩展建议

1. **添加用户认证** - 如需公网部署
2. **数据库持久化** - 替换内存存储
3. **批量下载** - 播放列表支持
4. **下载队列** - 限制并发数量
5. **文件管理** - 更丰富的文件操作

## 注意事项

- 仅限个人使用，请遵守各平台的服务条款
- 建议在局域网环境下使用
- 下载大文件时注意磁盘空间
- 定期清理下载文件和任务历史

## 许可证

本项目使用 MIT 许可证 - 详见 LICENSE 文件