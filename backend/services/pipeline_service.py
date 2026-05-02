"""
流水线服务 - 集成现有的Agent系统
"""
import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional
import uuid
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.pipeline_executor import PipelineExecutor
from backend.websocket.manager import manager
from backend.utils.logger import pipeline_logger, log_pipeline_event, log_error

class PipelineService:
    def __init__(self):
        # pipeline_id -> pipeline_info
        self.pipelines: Dict[str, dict] = {}
        # 运行中的任务
        self.running_tasks: Dict[str, asyncio.Task] = {}
        pipeline_logger.info("PipelineService初始化完成")

    def create_pipeline(self, image_path: str, config: dict) -> str:
        """创建新的流水线"""
        pipeline_id = str(uuid.uuid4())
        
        self.pipelines[pipeline_id] = {
            "id": pipeline_id,
            "image_path": image_path,
            "config": config,
            "status": "idle",
            "current_round": 0,
            "agents": [
                {"id": "agent1", "status": "idle", "task": None, "progress": None, "message": None},
                {"id": "agent2", "status": "idle", "task": None, "progress": None, "message": None},
                {"id": "agent3", "status": "idle", "task": None, "progress": None, "message": None},
                {"id": "agent4", "status": "idle", "task": None, "progress": None, "message": None},
            ],
            "results": None,
            "created_at": datetime.now(),
            "output_dir": f"storage/outputs/{pipeline_id}"
        }
        
        # 创建输出目录
        os.makedirs(self.pipelines[pipeline_id]["output_dir"], exist_ok=True)
        
        log_pipeline_event(pipeline_id, "创建", f"image={image_path}, config={config}")
        
        return pipeline_id

    async def start_pipeline(self, pipeline_id: str):
        """启动流水线"""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        pipeline["status"] = "running"
        
        log_pipeline_event(pipeline_id, "启动", f"max_loops={pipeline['config']['max_loops']}")
        
        # 创建异步任务
        task = asyncio.create_task(self._run_pipeline(pipeline_id))
        self.running_tasks[pipeline_id] = task

    async def _run_pipeline(self, pipeline_id: str):
        """运行流水线的异步任务"""
        pipeline = self.pipelines[pipeline_id]
        
        try:
            log_pipeline_event(pipeline_id, "开始执行", "")
            
            # 发送开始消息
            await manager.send_message(pipeline_id, "pipeline_start", {
                "pipeline_id": pipeline_id,
                "message": "流水线已启动"
            })
            
            # 创建执行器
            executor = PipelineExecutor(pipeline_id)
            
            # 创建一个任务来定期处理状态更新
            async def process_status_updates():
                """定期处理状态更新队列"""
                while pipeline["status"] == "running":
                    updates = executor.get_pending_updates()
                    for update in updates:
                        if update.get("type") == "progress":
                            # 进度更新
                            pipeline["current_round"] = update["round"]
                            await manager.send_message(pipeline_id, "progress_update", {
                                "round": update["round"],
                                "max_rounds": update["max_rounds"]
                            })
                        else:
                            # Agent状态更新
                            agent_id = update["agent_id"]
                            # 更新pipeline中的agent状态
                            for agent in pipeline["agents"]:
                                if agent["id"] == agent_id:
                                    agent["status"] = update["status"]
                                    agent["task"] = update.get("task")
                                    agent["progress"] = update.get("progress")
                                    agent["message"] = update.get("message")
                                    break
                            
                            # 发送WebSocket消息
                            await manager.send_message(pipeline_id, "agent_status", update)
                    
                    await asyncio.sleep(0.1)  # 每100ms检查一次
            
            # 启动状态更新处理任务
            update_task = asyncio.create_task(process_status_updates())
            
            # 在线程池中运行同步的pipeline
            loop = asyncio.get_event_loop()
            success, code_path, image_path, summary = await loop.run_in_executor(
                None,
                executor.run_full_pipeline,
                pipeline["image_path"],
                pipeline["output_dir"],
                pipeline["config"]["max_loops"],
                pipeline["config"]["threshold"],
                pipeline["config"]["strict_mode"]
            )
            
            # 更新结果
            pipeline["status"] = "completed" if success else "failed"
            pipeline["results"] = {
                "success": success,
                "code_path": code_path,
                "image_path": image_path,
                "summary": summary
            }
            
            # 给一点时间让最后的状态更新发送出去
            await asyncio.sleep(0.3)
            
            # 停止状态更新任务
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass
            
            # 处理剩余的状态更新（确保所有更新都发送）
            updates = executor.get_pending_updates()
            for update in updates:
                if update.get("type") == "progress":
                    pipeline["current_round"] = update["round"]
                    await manager.send_message(pipeline_id, "progress_update", {
                        "round": update["round"],
                        "max_rounds": update["max_rounds"]
                    })
                else:
                    agent_id = update["agent_id"]
                    for agent in pipeline["agents"]:
                        if agent["id"] == agent_id:
                            agent["status"] = update["status"]
                            agent["task"] = update.get("task")
                            agent["progress"] = update.get("progress")
                            agent["message"] = update.get("message")
                            break
                    await manager.send_message(pipeline_id, "agent_status", update)
            
            # 再等待一下确保WebSocket消息都发送完毕
            await asyncio.sleep(0.2)
            
            log_pipeline_event(
                pipeline_id, 
                "执行完成" if success else "执行失败", 
                f"success={success}, summary={summary}"
            )
            
            # 发送完成消息
            await manager.send_message(pipeline_id, "pipeline_complete", {
                "pipeline_id": pipeline_id,
                "success": success,
                "message": "流水线执行完成" if success else "流水线执行失败"
            })
            
        except Exception as e:
            pipeline["status"] = "failed"
            log_error(e, f"流水线执行 {pipeline_id}")
            
            # 停止状态更新任务
            if 'update_task' in locals():
                update_task.cancel()
                try:
                    await update_task
                except asyncio.CancelledError:
                    pass
            
            # 发送错误消息
            await manager.send_message(pipeline_id, "pipeline_error", {
                "pipeline_id": pipeline_id,
                "message": str(e)
            })
        finally:
            if pipeline_id in self.running_tasks:
                del self.running_tasks[pipeline_id]

    def _run_agent_pipeline_sync(self, pipeline_id: str):
        """同步运行agent pipeline（在线程池中执行）- 已弃用，使用PipelineExecutor代替"""
        # 此方法已被PipelineExecutor取代，保留以防需要回退
        pass

    async def stop_pipeline(self, pipeline_id: str):
        """停止流水线"""
        if pipeline_id in self.running_tasks:
            task = self.running_tasks[pipeline_id]
            task.cancel()
            
            pipeline = self.pipelines[pipeline_id]
            pipeline["status"] = "stopped"
            
            log_pipeline_event(pipeline_id, "停止", "用户手动停止")
            
            await manager.send_message(pipeline_id, "pipeline_stop", {
                "pipeline_id": pipeline_id,
                "message": "流水线已停止"
            })

    def get_pipeline_status(self, pipeline_id: str) -> Optional[dict]:
        """获取流水线状态"""
        return self.pipelines.get(pipeline_id)

    def get_all_pipelines(self) -> list:
        """获取所有流水线"""
        return list(self.pipelines.values())

# 全局服务实例
pipeline_service = PipelineService()
