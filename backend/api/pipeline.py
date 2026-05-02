"""
流水线管理API
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import PipelineConfig, PipelineStartResponse, PipelineStatus
from backend.services.pipeline_service import pipeline_service
from backend.utils.logger import api_logger, log_error

router = APIRouter()

@router.post("/pipeline/start", response_model=PipelineStartResponse)
async def start_pipeline(config: PipelineConfig):
    """
    启动流水线
    """
    api_logger.info(f"启动流水线请求: image={config.image_path}, max_loops={config.max_loops}, threshold={config.threshold}")
    
    try:
        # 创建流水线
        pipeline_id = pipeline_service.create_pipeline(
            image_path=config.image_path,
            config={
                "max_loops": config.max_loops,
                "threshold": config.threshold,
                "strict_mode": config.strict_mode
            }
        )
        
        api_logger.info(f"流水线已创建: {pipeline_id}")
        
        # 启动流水线
        await pipeline_service.start_pipeline(pipeline_id)
        
        api_logger.info(f"流水线已启动: {pipeline_id}")
        
        return PipelineStartResponse(
            pipeline_id=pipeline_id,
            status="running",
            message="流水线已启动"
        )
    except Exception as e:
        log_error(e, "启动流水线")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")

@router.get("/pipeline/{pipeline_id}/status", response_model=PipelineStatus)
async def get_pipeline_status(pipeline_id: str):
    """
    获取流水线状态
    """
    api_logger.debug(f"查询流水线状态: {pipeline_id}")
    
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        api_logger.warning(f"流水线不存在: {pipeline_id}")
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    return PipelineStatus(
        pipeline_id=pipeline["id"],
        status=pipeline["status"],
        current_round=pipeline["current_round"],
        max_rounds=pipeline["config"]["max_loops"],
        agents=pipeline["agents"]
    )

@router.post("/pipeline/{pipeline_id}/stop")
async def stop_pipeline(pipeline_id: str):
    """
    停止流水线
    """
    api_logger.info(f"停止流水线请求: {pipeline_id}")
    
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        api_logger.warning(f"流水线不存在: {pipeline_id}")
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    if pipeline["status"] != "running":
        api_logger.warning(f"流水线未在运行: {pipeline_id}, status={pipeline['status']}")
        raise HTTPException(status_code=400, detail="流水线未在运行")
    
    try:
        await pipeline_service.stop_pipeline(pipeline_id)
        api_logger.info(f"流水线已停止: {pipeline_id}")
        return {"message": "流水线已停止"}
    except Exception as e:
        log_error(e, f"停止流水线 {pipeline_id}")
        raise HTTPException(status_code=500, detail=f"停止失败: {str(e)}")
