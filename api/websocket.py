from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
import logging
from api.models import ProgressUpdate, JobStatusResponse

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储活跃的 WebSocket 连接
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            'client_id': client_id,
            'connected_at': asyncio.get_event_loop().time()
        }
        logger.info(f"WebSocket connected: {client_id or 'anonymous'}")
    
    def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            client_info = self.connection_info.pop(websocket, {})
            client_id = client_info.get('client_id', 'anonymous')
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送消息给特定连接"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_job_update(self, job_id: str, job_status: JobStatusResponse):
        """发送任务更新"""
        message = {
            'type': 'job_update',
            'job_id': job_id,
            'data': {
                'job_id': job_status.job_id,
                'status': job_status.status.value,
                'progress': job_status.progress,
                'speed': job_status.speed,
                'eta': job_status.eta,
                'title': job_status.title,
                'filename': job_status.filename,
                'error_message': job_status.error_message,
                'updated_at': job_status.updated_at.isoformat()
            }
        }
        await self.broadcast(message)
    
    async def send_system_message(self, message: str, level: str = "info"):
        """发送系统消息"""
        system_message = {
            'type': 'system_message',
            'level': level,  # info, warning, error, success
            'message': message,
            'timestamp': asyncio.get_event_loop().time()
        }
        await self.broadcast(system_message)
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)
    
    def get_connection_info(self) -> List[Dict]:
        """获取连接信息"""
        current_time = asyncio.get_event_loop().time()
        return [
            {
                'client_id': info.get('client_id', 'anonymous'),
                'connected_duration': current_time - info.get('connected_at', current_time)
            }
            for info in self.connection_info.values()
        ]

# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点处理函数"""
    client_id = None
    
    try:
        await websocket_manager.connect(websocket)
        
        # 发送欢迎消息
        await websocket_manager.send_personal_message({
            'type': 'welcome',
            'message': '连接成功！您将收到实时下载进度更新。',
            'connection_count': websocket_manager.get_connection_count()
        }, websocket)
        
        # 保持连接活跃，监听客户端消息
        while True:
            try:
                # 等待客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理客户端消息
                message_type = message.get('type')
                
                if message_type == 'ping':
                    # 心跳检测
                    await websocket_manager.send_personal_message({
                        'type': 'pong',
                        'timestamp': asyncio.get_event_loop().time()
                    }, websocket)
                
                elif message_type == 'set_client_id':
                    # 设置客户端ID
                    client_id = message.get('client_id')
                    if websocket in websocket_manager.connection_info:
                        websocket_manager.connection_info[websocket]['client_id'] = client_id
                        logger.info(f"Client ID set: {client_id}")
                
                elif message_type == 'get_status':
                    # 请求状态信息
                    await websocket_manager.send_personal_message({
                        'type': 'status_info',
                        'connection_count': websocket_manager.get_connection_count(),
                        'connections': websocket_manager.get_connection_info()
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    'type': 'error',
                    'message': '无效的 JSON 格式'
                }, websocket)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket_manager.send_personal_message({
                    'type': 'error',
                    'message': '处理消息时发生错误'
                }, websocket)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)

# 创建一个回调函数供 JobManager 使用
async def job_progress_callback(job_id: str, job_status: JobStatusResponse):
    """任务进度回调函数"""
    await websocket_manager.send_job_update(job_id, job_status)