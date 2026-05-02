"""
结果查询API
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ResultsResponse, ValidationDimensions, Report
from backend.services.pipeline_service import pipeline_service
from backend.services.storage_service import storage_service
from backend.config import BASE_URL
import re

router = APIRouter()

@router.get("/results/{pipeline_id}", response_model=ResultsResponse)
async def get_results(pipeline_id: str, round: int = None):
    """
    获取流水线结果
    """
    pipeline = pipeline_service.get_pipeline_status(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    if pipeline["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="流水线尚未完成")
    
    try:
        # 获取输出文件
        files = storage_service.get_output_files(pipeline_id)
        
        # 读取代码
        code = ""
        if "code" in files:
            code = storage_service.read_file(files["code"])
        
        # 图片URL - 返回完整URL
        image_url = f"{BASE_URL}/outputs/{pipeline_id}/generated_chart.png" if "image" in files else ""
        
        # 读取报告
        reports = []
        if "reports" in files:
            for report_file in files["reports"]:
                content = storage_service.read_file(report_file)
                filename = report_file.split("/")[-1]
                reports.append(Report(
                    title=filename.replace(".txt", "").replace("_", " "),
                    timestamp=pipeline["created_at"].isoformat(),
                    content=content
                ))
        
        # 解析验证结果
        dimensions = ValidationDimensions(color=0, text=0, structure=0, vlm=0)
        score = 0.0
        passed = False
        
        if "validators" in files and files["validators"]:
            # 读取最后一个验证文件
            validator_content = storage_service.read_file(files["validators"][-1])
            
            # 解析分数 - 从 "score=0.6931" 或 "final=0.693" 格式中提取
            score_match = re.search(r"score=([\d.]+)", validator_content)
            if score_match:
                score = float(score_match.group(1))
            else:
                # 尝试从 final= 中提取
                final_match = re.search(r"final=([\d.]+)", validator_content)
                if final_match:
                    score = float(final_match.group(1))
            
            # 解析通过状态
            passed_match = re.search(r"pass=(True|False)", validator_content)
            if passed_match:
                passed = passed_match.group(1) == "True"
            
            # 解析各维度分数
            # 格式: color=0.820(global=0.890, block=0.780, hsv=0.788)
            # 注意：要匹配后面带括号的评分，而不是前面 w(...) 中的权重
            # 使用更精确的正则表达式：匹配 "| color=数字(" 或 "color=数字(详细"
            color_match = re.search(r"\|\s*color=([\d.]+)\(", validator_content)
            text_match = re.search(r"\|\s*text=([\d.]+)\(", validator_content)
            struct_match = re.search(r"\|\s*struct=([\d.]+)\(", validator_content)
            
            # 如果上面的匹配失败，尝试更宽松的匹配（向后查找带括号的）
            if not color_match:
                color_match = re.search(r"color=([\d.]+)\([^)]*global=", validator_content)
            if not text_match:
                text_match = re.search(r"text=([\d.]+)\([^)]*bleu=", validator_content)
            if not struct_match:
                struct_match = re.search(r"struct=([\d.]+)\([^)]*ssim=", validator_content)
            
            dimensions = ValidationDimensions(
                color=float(color_match.group(1)) if color_match else score,
                text=float(text_match.group(1)) if text_match else score,
                structure=float(struct_match.group(1)) if struct_match else score,
                vlm=score  # VLM分数使用总分
            )
        
        return ResultsResponse(
            pipeline_id=pipeline_id,
            code=code,
            image_url=image_url,
            score=score,
            passed=passed,
            dimensions=dimensions,
            reports=reports
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")
