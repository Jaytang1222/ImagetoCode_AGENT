"""
文件存储服务
"""
import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime

from backend.config import UPLOAD_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS

class StorageService:
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.output_dir = OUTPUT_DIR

    def save_upload_file(self, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        保存上传的文件
        返回: (文件路径, 文件名)
        """
        # 验证文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}")
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = self.upload_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path), unique_filename

    def get_file_path(self, filename: str, directory: str = "uploads") -> Optional[Path]:
        """获取文件路径"""
        if directory == "uploads":
            file_path = self.upload_dir / filename
        else:
            file_path = self.output_dir / filename
        
        if file_path.exists():
            return file_path
        return None

    def delete_file(self, filename: str, directory: str = "uploads"):
        """删除文件"""
        file_path = self.get_file_path(filename, directory)
        if file_path and file_path.exists():
            os.remove(file_path)

    def delete_directory(self, dir_name: str):
        """删除目录"""
        dir_path = self.output_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)

    def get_output_files(self, pipeline_id: str) -> dict:
        """获取流水线输出文件"""
        output_dir = self.output_dir / pipeline_id
        
        if not output_dir.exists():
            return {}
        
        files = {}
        
        # 查找代码文件
        code_file = output_dir / "current_matplotlib.py"
        if code_file.exists():
            files["code"] = str(code_file)
        
        # 查找生成的图片
        image_file = output_dir / "generated_chart.png"
        if image_file.exists():
            files["image"] = str(image_file)
        
        # 查找报告文件
        report_files = list(output_dir.glob("report_*.txt"))
        files["reports"] = [str(f) for f in sorted(report_files)]
        
        # 查找验证结果（txt格式）
        validator_files = list(output_dir.glob("validator_*.txt"))
        files["validators"] = [str(f) for f in sorted(validator_files)]
        
        # 查找验证结果（json格式）
        validator_json_files = list(output_dir.glob("validator_*.json"))
        files["validators_json"] = [str(f) for f in sorted(validator_json_files)]
        
        return files

    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        return os.path.getsize(file_path)

# 全局服务实例
storage_service = StorageService()
