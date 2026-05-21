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
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))
BASE_URL = os.getenv("BASE_URL", f"http://{SERVER_HOST}:{SERVER_PORT}")

# API配置 - 多模型支持
# 当前使用的模型提供商 (qwen, openai, gemini, doubao)
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "qwen")

# 各提供商的 API Key
QWEN_API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")  # 兼容旧配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# OpenAI 兼容的自定义 Base URL (可选)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
# 豆包自定义 Base URL (可选)
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# 默认模型名称（已弃用，每个提供商使用自己的默认模型）
# DEFAULT_VLM_MODEL = os.getenv("DEFAULT_VLM_MODEL", "qwen3.5-plus")
# DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "qwen-plus")

# 其他配置
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

# 兼容性：保留旧的变量名
DASHSCOPE_API_KEY = QWEN_API_KEY

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
