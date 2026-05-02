"""
配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
BASE_URL = os.getenv("BASE_URL", f"http://{SERVER_HOST}:{SERVER_PORT}")

# API配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

# 文件存储配置
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
OUTPUT_DIR = BASE_DIR / "storage" / "outputs"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 确保目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# 流水线默认配置
DEFAULT_MAX_LOOPS = 5
DEFAULT_THRESHOLD = 0.75
DEFAULT_STRICT_MODE = True
