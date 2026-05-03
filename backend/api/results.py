"""
结果查询API
"""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ResultsResponse, ValidationDimensions, Report
from backend.services.pipeline_service import pipeline_service
from backend.services.storage_service import storage_service
from backend.config import BASE_URL
import json
import os

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
        
        # 解析验证结果 - 优先使用 JSON 格式
        dimensions = ValidationDimensions(color=0, text=0, structure=0, vlm=0)
        score = 0.0
        passed = False
        
        # 优先使用 JSON 格式的验证结果
        if "validators_json" in files and files["validators_json"]:
            try:
                json_file = files["validators_json"][-1]  # 使用最后一轮的结果
                json_content = storage_service.read_file(json_file)
                validator_data = json.loads(json_content)
                
                # 从结构化数据中提取信息
                score = validator_data.get("final_score", 0.0)
                passed = validator_data.get("pass", False)
                
                detailed = validator_data.get("detailed_result", {})
                dims = detailed.get("dimensions", {})
                
                dimensions = ValidationDimensions(
                    color=dims.get("color", 0.0),
                    text=dims.get("text", 0.0),
                    structure=dims.get("structure", 0.0),
                    vlm=dims.get("vlm", 0.0)
                )
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                # JSON 解析失败，降级到文本解析
                print(f"JSON 解析失败，降级到文本解析: {e}")
                if "validators" in files and files["validators"]:
                    validator_content = storage_service.read_file(files["validators"][-1])
                    dimensions, score, passed = _parse_validator_text(validator_content)
        elif "validators" in files and files["validators"]:
            # 没有 JSON 文件，使用文本解析（向后兼容）
            validator_content = storage_service.read_file(files["validators"][-1])
            dimensions, score, passed = _parse_validator_text(validator_content)
        
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


def _parse_validator_text(validator_content: str) -> tuple:
    """
    从文本格式的验证器输出中解析结果（向后兼容）
    返回: (dimensions, score, passed)
    """
    import re
    
    dimensions = ValidationDimensions(color=0, text=0, structure=0, vlm=0)
    score = 0.0
    passed = False
    
    # 解析分数 - 从 "final_score=0.6931" 格式中提取
    score_match = re.search(r"final_score=([\d.]+)", validator_content)
    if score_match:
        score = float(score_match.group(1))
    else:
        # 尝试从旧格式 "score=" 中提取
        score_match = re.search(r"(?:^|\n)score=([\d.]+)", validator_content)
        if score_match:
            score = float(score_match.group(1))
    
    # 解析通过状态
    passed_match = re.search(r"pass=(True|False)", validator_content)
    if passed_match:
        passed = passed_match.group(1) == "True"
    
    # 解析各维度分数
    # 使用更精确的正则：匹配后面带详细指标的分数
    # 格式: color=0.820(global=0.890, block=0.780, hsv=0.788)
    color_match = re.search(r"color=([\d.]+)\([^)]*(?:global|block|hsv)=", validator_content)
    text_match = re.search(r"text=([\d.]+)\([^)]*(?:bleu|layout|cov)=", validator_content)
    struct_match = re.search(r"struct=([\d.]+)\([^)]*(?:ssim|topo|dist)=", validator_content)
    
    # VLM 分数可能没有详细指标，使用总分作为降级
    vlm_score = score
    
    dimensions = ValidationDimensions(
        color=float(color_match.group(1)) if color_match else score * 0.8,
        text=float(text_match.group(1)) if text_match else score * 0.8,
        structure=float(struct_match.group(1)) if struct_match else score * 0.8,
        vlm=vlm_score
    )
    
    return dimensions, score, passed
