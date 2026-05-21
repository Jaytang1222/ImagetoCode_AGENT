"""
增强的流水线执行器 - 带状态更新回调
"""
import os
import json
from pathlib import Path
from typing import Optional, Tuple, Callable
from src.agents.agent1_code_generation import Agent1Preset, agent1_generate_and_dispatch
from src.agents.agent2_visual_judgment import agent2_chart_evaluation_report
from src.agents.agent3_code_evaluation import agent3_code_evaluation_report
from src.agents.agent4_feedback_revision import agent4_feedback_optimize_code
from src.utils.matplotlib_render import render_matplotlib_code_to_png
from src.validators.multidim_validator import multidimensional_validate
from backend.utils.logger import pipeline_logger


class PipelineExecutor:
    """带状态回调的流水线执行器"""
    
    def __init__(self, pipeline_id: str, status_callback: Optional[Callable] = None):
        self.pipeline_id = pipeline_id
        self.status_callback = status_callback
        self.status_queue = []  # 用于存储状态更新，由主线程处理
        
    def _queue_status(self, data: dict):
        """将状态更新加入队列"""
        self.status_queue.append(data)
    
    def _send_status(self, agent_id: str, status: str, task: str = None, progress: float = None, message: str = None):
        """发送agent状态更新"""
        self._queue_status({
            "type": "agent_status",
            "agent_id": agent_id,
            "status": status,
            "task": task,
            "progress": progress,
            "message": message
        })
    
    def _send_progress(self, current_round: int, max_rounds: int):
        """发送进度更新"""
        self._queue_status({
            "type": "progress",
            "round": current_round,
            "max_rounds": max_rounds
        })
    
    def get_pending_updates(self):
        """获取并清空待处理的状态更新"""
        updates = self.status_queue.copy()
        self.status_queue.clear()
        return updates
    
    def run_full_pipeline(
        self,
        input_chart_image: str,
        out_dir: str = "outputs",
        max_loops: int = 5,
        threshold: float = 0.75,
        model_provider: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[str], str]:
        """
        执行完整流水线，带状态更新
        
        Args:
            input_chart_image: 输入图表路径
            out_dir: 输出目录
            max_loops: 最大迭代轮数
            threshold: 验证通过阈值
            model_provider: 模型提供商 (qwen, openai, claude, gemini, deepseek, glm)
        
        返回 (是否验证通过, 最终代码路径, 最终渲染PNG路径, 最后一轮说明摘要)
        """
        # 设置模型配置环境变量（如果提供）
        original_env = {}
        
        # 解析模型配置
        agent1_vlm = agent2_vlm = validator_vlm = None
        agent3_llm = agent4_llm = None
        actual_provider = model_provider
        
        if model_provider == "recommended":
            actual_provider = "qwen"
            agent1_vlm = "qwen3.6-plus"
            agent2_vlm = "qwen3.6-flash"
            agent3_llm = "deepseek-v4-flash"
            agent4_llm = "deepseek-v4-flash"
            validator_vlm = "qwen3.6-flash"
            pipeline_logger.info(
                f"[{self.pipeline_id}] 使用推荐模型: "
                f"Agent1=qwen3.6-plus, Agent2/Validator=qwen3.6-flash, Agent3/4=deepseek-v4-flash"
            )
        
        if actual_provider:
            original_env["MODEL_PROVIDER"] = os.environ.get("MODEL_PROVIDER")
            os.environ["MODEL_PROVIDER"] = actual_provider
            pipeline_logger.info(f"[{self.pipeline_id}] 使用模型提供商: {actual_provider}")
        
        try:
            return self._run_pipeline_internal(
                input_chart_image, out_dir, max_loops, threshold,
                agent1_vlm=agent1_vlm, agent2_vlm=agent2_vlm,
                agent3_llm=agent3_llm, agent4_llm=agent4_llm,
                validator_vlm=validator_vlm,
            )
        finally:
            # 恢复原始环境变量
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    def _run_pipeline_internal(
        self,
        input_chart_image: str,
        out_dir: str,
        max_loops: int,
        threshold: float,
        agent1_vlm: Optional[str] = None,
        agent2_vlm: Optional[str] = None,
        agent3_llm: Optional[str] = None,
        agent4_llm: Optional[str] = None,
        validator_vlm: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[str], str]:
        """内部流水线执行逻辑"""
        os.makedirs(out_dir, exist_ok=True)
        code_path = os.path.join(out_dir, "current_matplotlib.py")
        gen_png = os.path.join(out_dir, "generated_chart.png")

        last_summary = ""
        code: Optional[str] = None
        cached_chart_type: Optional[str] = None

        for loop in range(max_loops):
            pipeline_logger.info(f"[{self.pipeline_id}] 第 {loop + 1}/{max_loops} 轮")
            
            # 更新进度
            self._send_progress(loop + 1, max_loops)

            if loop == 0:
                # Agent1: 首轮代码生成
                self._send_status("agent1", "running", "代码生成", 0.0, "正在生成代码...")
                
                try:
                    agent1_result = agent1_generate_and_dispatch(
                        input_chart_image_path=input_chart_image,
                        preset=Agent1Preset(out_dir=out_dir, dispatch_to_agents=False),
                        extra_feedback=None,
                        vlm_model=agent1_vlm,
                    )
                    code = agent1_result.generated_code
                    
                    self._send_status("agent1", "completed", "代码生成完成", 1.0, "代码已生成")
                except Exception as e:
                    error_msg = f"代码生成失败: {str(e)}"
                    self._send_status("agent1", "error", None, None, error_msg)
                    pipeline_logger.error(f"[{self.pipeline_id}] {error_msg}")
                    return False, code_path, None, error_msg
            else:
                pipeline_logger.info(f"[{self.pipeline_id}] 在上一轮 Agent4 输出上继续优化")

            Path(code_path).write_text(code, encoding="utf-8")
            
            # 渲染代码（所有轮次都显示渲染状态）
            if loop == 0:
                self._send_status("agent1", "running", "渲染图表", 0.5, "正在渲染...")
            else:
                # 第2+轮也显示渲染状态，但不占用 Agent1
                pipeline_logger.info(f"[{self.pipeline_id}] 渲染当前代码")
            
            png, error = render_matplotlib_code_to_png(code, gen_png)
            if not png:
                msg = f"无法生成复现图 PNG。错误: {error}"
                if loop == 0:
                    self._send_status("agent1", "error", None, None, msg)
                pipeline_logger.error(f"[{self.pipeline_id}] {msg}")
                last_summary = msg
                return False, code_path, None, last_summary
            
            if loop == 0:
                self._send_status("agent1", "completed", "渲染完成", 1.0, "图表已渲染")

            # Agent2: 视觉评判
            self._send_status("agent2", "running", "视觉评判", 0.0, "正在对比图表...")
            
            try:
                chart_report = agent2_chart_evaluation_report(input_chart_image, png, vlm_model=agent2_vlm)
                Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                    chart_report, encoding="utf-8"
                )
                self._send_status("agent2", "completed", "视觉评判完成", 1.0, "评判已完成")
            except Exception as e:
                error_msg = f"视觉评判失败: {str(e)}"
                self._send_status("agent2", "error", None, None, error_msg)
                pipeline_logger.error(f"[{self.pipeline_id}] {error_msg}")
                return False, code_path, None, error_msg

            # Agent3: 代码评判
            self._send_status("agent3", "running", "代码评判", 0.0, "正在评估代码...")
            
            try:
                code_report = agent3_code_evaluation_report(code, chart_report, llm_model=agent3_llm)
                Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                    code_report, encoding="utf-8"
                )
                self._send_status("agent3", "completed", "代码评判完成", 1.0, "评判已完成")
            except Exception as e:
                error_msg = f"代码评判失败: {str(e)}"
                self._send_status("agent3", "error", None, None, error_msg)
                pipeline_logger.error(f"[{self.pipeline_id}] {error_msg}")
                return False, code_path, None, error_msg

            # Agent4: 反馈优化
            self._send_status("agent4", "running", "代码优化", 0.0, "正在优化代码...")
            
            try:
                code_new = agent4_feedback_optimize_code(code, code_report, chart_report, llm_model=agent4_llm)
                Path(
                    os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
                ).write_text(code_new, encoding="utf-8")
                
                # 渲染 Agent4 优化后的代码（在标记 completed 之前）
                self._send_status("agent4", "running", "渲染优化后的图表", 0.8, "正在渲染...")
                png_final, error = render_matplotlib_code_to_png(code_new, gen_png)
                if not png_final:
                    last_summary = f"Agent4 后截图失败: {error}"
                    self._send_status("agent4", "error", None, None, last_summary)
                    pipeline_logger.error(f"[{self.pipeline_id}] {last_summary}")
                    return False, code_path, None, last_summary
                
                # 渲染成功后才标记为 completed
                self._send_status("agent4", "completed", "代码优化完成", 1.0, "优化已完成")
            except Exception as e:
                error_msg = f"代码优化失败: {str(e)}"
                self._send_status("agent4", "error", None, None, error_msg)
                pipeline_logger.error(f"[{self.pipeline_id}] {error_msg}")
                return False, code_path, None, error_msg

            # 多维验证
            pipeline_logger.info(f"[{self.pipeline_id}] 多维验证器对比原图与复现图")
            ok, score, last_summary, detailed_result = multidimensional_validate(
                input_chart_image, 
                png_final, 
                threshold=threshold,
                chart_report=chart_report,
                code_report=code_report,
                vlm_model=validator_vlm,
                current_code=code,
                cached_chart_type=cached_chart_type,
            )
            pipeline_logger.info(f"[{self.pipeline_id}] 验证结果: score={score:.4f} pass={ok} | {last_summary}")
            
            # 缓存图表类型供后续轮次复用（避免重复 VLM 调用）
            if cached_chart_type is None:
                cached_chart_type = detailed_result.get("chart_type", "unknown")

            # 保存结构化的验证结果
            validator_output = {
                "pass": ok,
                "final_score": score,
                "round": loop + 1,
                "summary": last_summary,
                "detailed_result": detailed_result
            }
            
            # 保存 JSON 格式（主要用于程序读取）
            Path(os.path.join(out_dir, f"validator_round{loop+1}.json")).write_text(
                json.dumps(validator_output, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            
            # 保存文本格式（用于人类阅读和向后兼容）
            validator_content = f"pass={ok}\nfinal_score={score:.6f}\nround={loop+1}\n\n{last_summary}"
            Path(os.path.join(out_dir, f"validator_round{loop+1}.txt")).write_text(
                validator_content,
                encoding="utf-8",
            )

            if ok:
                Path(code_path).write_text(code_new, encoding="utf-8")
                pipeline_logger.info(f"[{self.pipeline_id}] 验证通过，最终代码已写入: {code_path}")
                return True, code_path, png_final, last_summary

            code = code_new

        pipeline_logger.info(f"[{self.pipeline_id}] 未能在限定轮数内通过验证，返回最后一版代码")
        Path(code_path).write_text(code, encoding="utf-8")
        return False, code_path, gen_png, last_summary
