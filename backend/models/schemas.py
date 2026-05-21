"""
Pydantic数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# 上传响应
class UploadResponse(BaseModel):
    path: str
    filename: str
    size: int

# 流水线配置
class PipelineConfig(BaseModel):
    model_config = {"protected_namespaces": ()}  # 允许 model_ 前缀
    
    image_path: str
    max_loops: int = Field(default=5, ge=1, le=10)
    threshold: float = Field(default=0.75, ge=0, le=1)
    model_provider: Optional[str] = Field(default="qwen", description="模型提供商 (recommended, qwen, openai, gemini, doubao)")

# 流水线启动响应
class PipelineStartResponse(BaseModel):
    pipeline_id: str
    status: str
    message: str

# 流水线状态
class PipelineStatus(BaseModel):
    pipeline_id: str
    status: str  # idle, running, completed, failed
    current_round: int
    max_rounds: int
    agents: List[Dict]

# Agent状态
class AgentStatus(BaseModel):
    agent_id: str
    status: str  # idle, running, success, error
    task: Optional[str] = None
    progress: Optional[int] = None
    message: Optional[str] = None

# 验证维度
class ValidationDimensions(BaseModel):
    color: float
    text: float
    structure: float
    vlm: float

# 报告
class Report(BaseModel):
    title: str
    timestamp: str
    content: str

# 结果响应
class ResultsResponse(BaseModel):
    pipeline_id: str
    code: str
    image_url: str
    score: float
    passed: bool
    dimensions: ValidationDimensions
    reports: List[Report]

# 历史记录项
class HistoryItem(BaseModel):
    id: str
    filename: str
    timestamp: datetime
    rounds: int
    score: float
    status: str  # completed, failed, stopped

# 历史记录列表响应
class HistoryResponse(BaseModel):
    history: List[HistoryItem]

# WebSocket消息
class WSMessage(BaseModel):
    type: str
    payload: Dict
