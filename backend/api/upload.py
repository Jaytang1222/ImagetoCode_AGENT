"""
文件上传API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import UploadResponse
from backend.services.storage_service import storage_service
from backend.config import MAX_FILE_SIZE
from backend.utils.logger import api_logger, log_error

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    上传参考图表
    """
    api_logger.info(f"收到文件上传请求: {file.filename}")
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    
    api_logger.debug(f"文件大小: {file_size} bytes")
    
    if file_size > MAX_FILE_SIZE:
        api_logger.warning(f"文件大小超过限制: {file_size} > {MAX_FILE_SIZE}")
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024}MB)"
        )
    
    try:
        # 保存文件
        file_path, filename = storage_service.save_upload_file(content, file.filename)
        
        api_logger.info(f"文件上传成功: {filename} -> {file_path}")
        
        return UploadResponse(
            path=file_path,
            filename=filename,
            size=file_size
        )
    except ValueError as e:
        api_logger.error(f"文件验证失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(e, "文件上传")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
