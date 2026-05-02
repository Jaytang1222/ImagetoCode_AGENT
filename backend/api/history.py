"""
历史记录API
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import HistoryResponse, HistoryItem
from backend.services.pipeline_service import pipeline_service
from backend.services.storage_service import storage_service

router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
async def get_history():
    """
    获取所有历史记录
    """
    pipelines = pipeline_service.get_all_pipelines()
    
    # 只返回已完成或失败的流水线
    history_items = []
    for pipeline in pipelines:
        if pipeline["status"] in ["completed", "failed", "stopped"]:
            # 获取文件信息
            files = storage_service.get_output_files(pipeline["id"])
            
            # 从validator文件中提取分数
            score = 0.0
            if "validators" in files and files["validators"]:
                try:
                    # 读取最后一个验证文件
                    validator_content = storage_service.read_file(files["validators"][-1])
                    
                    # 优先解析 final_score= 格式（新格式）
                    import re
                    final_score_match = re.search(r"final_score=([\d.]+)", validator_content)
                    if final_score_match:
                        score = float(final_score_match.group(1))
                    else:
                        # 尝试从 final= 中提取（summary中的格式）
                        final_match = re.search(r"final=([\d.]+)", validator_content)
                        if final_match:
                            score = float(final_match.group(1))
                        else:
                            # 最后尝试从第二行的 score= 中提取（旧格式）
                            lines = validator_content.split('\n')
                            if len(lines) >= 2:
                                score_match = re.search(r"score=([\d.]+)", lines[1])
                                if score_match:
                                    score = float(score_match.group(1))
                except Exception as e:
                    print(f"解析分数失败: {e}")
                    score = 0.0
            
            # 获取原始文件名
            filename = pipeline["image_path"].split("/")[-1]
            
            history_items.append(HistoryItem(
                id=pipeline["id"],
                filename=filename,
                timestamp=pipeline["created_at"],
                rounds=pipeline["current_round"],
                score=score,
                status=pipeline["status"]
            ))
    
    # 按时间倒序排序
    history_items.sort(key=lambda x: x.timestamp, reverse=True)
    
    return HistoryResponse(history=history_items)

@router.delete("/history/{pipeline_id}")
async def delete_history(pipeline_id: str):
    """
    删除历史记录
    """
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    try:
        # 删除输出目录
        storage_service.delete_directory(pipeline_id)
        
        # 从内存中删除
        if pipeline_id in pipeline_service.pipelines:
            del pipeline_service.pipelines[pipeline_id]
        
        return {"message": "历史记录已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
