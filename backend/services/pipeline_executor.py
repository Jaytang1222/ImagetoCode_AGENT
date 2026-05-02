"""
增强的流水线执行器 - 带状态更新回调
"""
import os
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
        strict_algorithm_mode: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[str], str]:
        """
        执行完整流水线，带状态更新
        返回 (是否验证通过, 最终代码路径, 最终渲染PNG路径, 最后一轮说明摘要)
        """
        os.makedirs(out_dir, exist_ok=True)
        code_path = os.path.join(out_dir, "current_matplotlib.py")
        gen_png = os.path.join(out_dir, "generated_chart.png")

        last_summary = ""
        code: Optional[str] = None

        for loop in range(max_loops):
            pipeline_logger.info(f"[{self.pipeline_id}] 第 {loop + 1}/{max_loops} 轮")
            
            # 更新进度
            self._send_progress(loop + 1, max_loops)

            if strict_algorithm_mode:
                # Agent1: 代码生成 + 分发评审
                self._send_status("agent1", "running", "代码生成与分发评审", 0.0, "正在生成代码...")
                
                agent1_result = agent1_generate_and_dispatch(
                    input_chart_image_path=input_chart_image,
                    preset=Agent1Preset(out_dir=out_dir),
                    extra_feedback=None,
                )
                code = agent1_result.generated_code
                initial_chart_report = agent1_result.chart_report or ""
                initial_code_report = agent1_result.code_report or ""
                code_new = agent1_result.optimized_code or code
                
                if not code or not initial_chart_report or not initial_code_report:
                    last_summary = "严格模式下 Agent1 分发结果不完整"
                    self._send_status("agent1", "error", None, None, last_summary)
                    return False, code_path, None, last_summary
                
                Path(code_path).write_text(code, encoding="utf-8")
                Path(os.path.join(out_dir, f"report_agent2_initial_round{loop+1}.txt")).write_text(
                    initial_chart_report, encoding="utf-8"
                )
                Path(os.path.join(out_dir, f"report_agent3_initial_round{loop+1}.txt")).write_text(
                    initial_code_report, encoding="utf-8"
                )
                Path(
                    os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
                ).write_text(code_new, encoding="utf-8")
                
                self._send_status("agent1", "completed", "代码生成完成", 1.0, "代码已生成")
                self._send_status("agent2", "completed", "视觉评判完成", 1.0, "已完成评判")
                self._send_status("agent3", "completed", "代码评判完成", 1.0, "已完成评判")
                self._send_status("agent4", "completed", "代码优化完成", 1.0, "已完成优化")
                
            else:
                if loop == 0:
                    # Agent1: 首轮代码生成
                    self._send_status("agent1", "running", "代码生成", 0.0, "正在生成代码...")
                    
                    agent1_result = agent1_generate_and_dispatch(
                        input_chart_image_path=input_chart_image,
                        preset=Agent1Preset(out_dir=out_dir, dispatch_to_agents=False),
                        extra_feedback=None,
                    )
                    code = agent1_result.generated_code
                    
                    self._send_status("agent1", "completed", "代码生成完成", 1.0, "代码已生成")
                else:
                    pipeline_logger.info(f"[{self.pipeline_id}] 在上一轮 Agent4 输出上继续优化")

                Path(code_path).write_text(code, encoding="utf-8")
                
                # 渲染代码
                self._send_status("agent1", "running", "渲染图表", 0.5, "正在渲染...")
                png, error = render_matplotlib_code_to_png(code, gen_png)
                if not png:
                    msg = f"无法生成复现图 PNG。错误: {error}"
                    self._send_status("agent1", "error", None, None, msg)
                    last_summary = msg
                    return False, code_path, None, last_summary
                
                self._send_status("agent1", "completed", "渲染完成", 1.0, "图表已渲染")

                # Agent2: 视觉评判
                self._send_status("agent2", "running", "视觉评判", 0.0, "正在对比图表...")
                chart_report = agent2_chart_evaluation_report(input_chart_image, png)
                Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                    chart_report, encoding="utf-8"
                )
                self._send_status("agent2", "completed", "视觉评判完成", 1.0, "评判已完成")

                # Agent3: 代码评判
                self._send_status("agent3", "running", "代码评判", 0.0, "正在评估代码...")
                code_report = agent3_code_evaluation_report(code, chart_report)
                Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                    code_report, encoding="utf-8"
                )
                self._send_status("agent3", "completed", "代码评判完成", 1.0, "评判已完成")

                # Agent4: 反馈优化
                self._send_status("agent4", "running", "代码优化", 0.0, "正在优化代码...")
                code_new = agent4_feedback_optimize_code(code, code_report, chart_report)
                Path(
                    os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
                ).write_text(code_new, encoding="utf-8")
                self._send_status("agent4", "completed", "代码优化完成", 1.0, "优化已完成")

            # 渲染 Agent4 优化后的代码
            self._send_status("agent4", "running", "渲染优化后的图表", 0.5, "正在渲染...")
            png_final, error = render_matplotlib_code_to_png(code_new, gen_png)
            if not png_final:
                last_summary = f"Agent4 后截图失败: {error}"
                self._send_status("agent4", "error", None, None, last_summary)
                return False, code_path, None, last_summary

            # 重新评判优化后的结果
            self._send_status("agent2", "running", "重新评判优化结果", 0.0, "正在评判...")
            chart_report_final = agent2_chart_evaluation_report(input_chart_image, png_final)
            Path(os.path.join(out_dir, f"report_agent2_final_round{loop+1}.txt")).write_text(
                chart_report_final, encoding="utf-8"
            )
            self._send_status("agent2", "completed", "评判完成", 1.0, "评判已完成")

            self._send_status("agent3", "running", "重新评判代码", 0.0, "正在评判...")
            code_report_final = agent3_code_evaluation_report(code_new, chart_report_final)
            Path(os.path.join(out_dir, f"report_agent3_final_round{loop+1}.txt")).write_text(
                code_report_final, encoding="utf-8"
            )
            self._send_status("agent3", "completed", "评判完成", 1.0, "评判已完成")

            # 多维验证
            pipeline_logger.info(f"[{self.pipeline_id}] 多维验证器对比原图与复现图")
            ok, score, last_summary = multidimensional_validate(
                input_chart_image, 
                png_final, 
                threshold=threshold,
                chart_report=chart_report_final,
                code_report=code_report_final,
            )
            pipeline_logger.info(f"[{self.pipeline_id}] 验证结果: score={score:.4f} pass={ok} | {last_summary}")

            # 保存验证结果，使用清晰的格式
            validator_content = f"pass={ok}\nfinal_score={score:.6f}\nround={loop+1}\n\n{last_summary}"
            Path(os.path.join(out_dir, f"validator_round{loop+1}.txt")).write_text(
                validator_content,
                encoding="utf-8",
            )

            if ok:
                Path(code_path).write_text(code_new, encoding="utf-8")
                pipeline_logger.info(f"[{self.pipeline_id}] 验证通过，最终代码已写入: {code_path}")
                
                # 确保所有状态更新都已发送
                self._send_status("agent1", "completed", "验证通过", 1.0, f"第{loop+1}轮验证通过")
                self._send_status("agent2", "completed", "验证通过", 1.0, f"得分: {score:.4f}")
                self._send_status("agent3", "completed", "验证通过", 1.0, "代码质量达标")
                self._send_status("agent4", "completed", "验证通过", 1.0, "优化完成")
                
                return True, code_path, png_final, last_summary

            code = code_new

        pipeline_logger.info(f"[{self.pipeline_id}] 未能在限定轮数内通过验证，返回最后一版代码")
        Path(code_path).write_text(code, encoding="utf-8")
        return False, code_path, gen_png, last_summary
