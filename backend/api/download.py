"""
文件下载API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.services.pipeline_service import pipeline_service
from backend.services.storage_service import storage_service

router = APIRouter()

@router.get("/download/{pipeline_id}/code")
async def download_code(pipeline_id: str):
    """
    下载生成的代码
    """
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    files = storage_service.get_output_files(pipeline_id)
    
    if "code" not in files:
        raise HTTPException(status_code=404, detail="代码文件不存在")
    
    return FileResponse(
        path=files["code"],
        filename="generated_chart.py",
        media_type="text/x-python"
    )

@router.get("/download/{pipeline_id}/report")
async def download_report(pipeline_id: str):
    """
    下载验证报告
    """
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    files = storage_service.get_output_files(pipeline_id)
    
    if "validators" not in files or not files["validators"]:
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    # 返回最后一个验证报告
    return FileResponse(
        path=files["validators"][-1],
        filename="validation_report.txt",
        media_type="text/plain"
    )

@router.get("/download/{pipeline_id}/image")
async def download_image(pipeline_id: str):
    """
    下载生成的图片
    """
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    files = storage_service.get_output_files(pipeline_id)
    
    if "image" not in files:
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    return FileResponse(
        path=files["image"],
        filename="generated_chart.png",
        media_type="image/png"
    )
