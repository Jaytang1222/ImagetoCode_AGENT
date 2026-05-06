"""
日志系统配置
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 创建logs目录
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建格式化器
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台处理器（彩色输出）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 所有日志
    all_log_file = LOGS_DIR / "app.log"
    file_handler = RotatingFileHandler(
        all_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 文件处理器 - 错误日志
    error_log_file = LOGS_DIR / "error.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

# 创建各模块的日志记录器
api_logger = setup_logger("api", logging.INFO)
pipeline_logger = setup_logger("pipeline", logging.DEBUG)
websocket_logger = setup_logger("websocket", logging.INFO)
storage_logger = setup_logger("storage", logging.INFO)

# 主应用日志记录器
app_logger = setup_logger("app", logging.INFO)

def log_request(method: str, path: str, status_code: int, duration: float):
    """记录HTTP请求"""
    api_logger.info(f"{method} {path} - {status_code} - {duration:.3f}s")

def log_error(error: Exception, context: str = ""):
    """记录错误"""
    app_logger.error(f"{context} - {type(error).__name__}: {str(error)}", exc_info=True)

def log_pipeline_event(pipeline_id: str, event: str, details: str = ""):
    """记录流水线事件"""
    pipeline_logger.info(f"[{pipeline_id}] {event} - {details}")

def log_websocket_event(pipeline_id: str, event: str, details: str = ""):
    """记录WebSocket事件"""
    websocket_logger.info(f"[{pipeline_id}] {event} - {details}")
