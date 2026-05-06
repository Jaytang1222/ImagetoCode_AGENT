"""
WebSocket连接管理器
"""
from fastapi import WebSocket
from typing import Dict
import json
from backend.utils.logger import websocket_logger, log_websocket_event

class ConnectionManager:
    def __init__(self):
        # pipeline_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        websocket_logger.info("WebSocket管理器初始化完成")

    async def connect(self, websocket: WebSocket, pipeline_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[pipeline_id] = websocket
        log_websocket_event(pipeline_id, "连接建立", f"当前连接数: {len(self.active_connections)}")

    def disconnect(self, pipeline_id: str):
        """断开WebSocket连接"""
        if pipeline_id in self.active_connections:
            del self.active_connections[pipeline_id]
            log_websocket_event(pipeline_id, "连接断开", f"剩余连接数: {len(self.active_connections)}")

    async def send_message(self, pipeline_id: str, message_type: str, payload: dict):
        """发送消息到指定的pipeline"""
        if pipeline_id in self.active_connections:
            websocket = self.active_connections[pipeline_id]
            try:
                message = {
                    "type": message_type,
                    "payload": payload
                }
                await websocket.send_json(message)
                websocket_logger.debug(f"[{pipeline_id}] 发送消息: {message_type}")
            except Exception as e:
                websocket_logger.error(f"[{pipeline_id}] 发送消息失败: {e}")
                self.disconnect(pipeline_id)

    async def broadcast(self, message_type: str, payload: dict):
        """广播消息到所有连接"""
        websocket_logger.info(f"广播消息: {message_type} 到 {len(self.active_connections)} 个连接")
        for pipeline_id in list(self.active_connections.keys()):
            await self.send_message(pipeline_id, message_type, payload)

# 全局管理器实例
manager = ConnectionManager()
