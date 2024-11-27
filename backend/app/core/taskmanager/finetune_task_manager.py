from typing import Dict, List, Optional, Any
import uuid
import asyncio
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from collections import deque

from app.core.finetune.finetune import FinetuneInterface
from app.core.finetune.finetune_parameters import FinetuneParameters

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    QUEUED = "queued"       # 已排队
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled"  # 已取消

@dataclass
class FinetuneTask:
    """微调任务信息"""
    task_id: str                    # 任务ID
    user_id: uuid.UUID             # 用户ID
    parameters_id: uuid.UUID       # 参数ID
    status: TaskStatus             # 任务状态
    created_at: datetime           # 创建时间
    started_at: Optional[datetime] = None  # 开始时间
    finished_at: Optional[datetime] = None # 完成时间
    job_id: Optional[str] = None          # K8s Job ID
    error_message: Optional[str] = None   # 错误信息

class FinetuneTaskManager:
    """微调任务管理器"""
    
    def __init__(
        self,
        finetune_service: FinetuneInterface,
        max_concurrent_tasks: int = 5,
        max_tasks_per_user: int = 3
    ):
        """
        初始化任务管理器
        
        Args:
            finetune_service: 微调服务接口
            max_concurrent_tasks: 最大并发任务数
            max_tasks_per_user: 每个用户最大任务数
        """
        self.finetune_service = finetune_service
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_tasks_per_user = max_tasks_per_user
        
        # 任务队列和运行中的任务
        self.task_queue = deque()  # 等待队列
        self.running_tasks: Dict[str, FinetuneTask] = {}  # 运行中的任务
        self.all_tasks: Dict[str, FinetuneTask] = {}  # 所有任务的历史记录
        
        # 用户任务计数
        self.user_task_counts: Dict[uuid.UUID, int] = {}
        
        # 任务调度锁
        self._schedule_lock = asyncio.Lock()
        
        # 启动任务调度器
        self.scheduler_task = asyncio.create_task(self._task_scheduler())

    async def submit_task(
        self,
        user_id: uuid.UUID,
        parameters_id: uuid.UUID
    ) -> str:
        """
        提交微调任务
        
        Args:
            user_id: 用户ID
            parameters_id: 参数ID
            
        Returns:
            task_id: 任务ID
            
        Raises:
            ValueError: 超出用户任务限制
        """
        async with self._schedule_lock:
            # 检查用户任务数量限制
            if self.user_task_counts.get(user_id, 0) >= self.max_tasks_per_user:
                raise ValueError(f"用户任务数超出限制 (最大 {self.max_tasks_per_user})")
            
            # 创建新任务
            task_id = str(uuid.uuid4())
            task = FinetuneTask(
                task_id=task_id,
                user_id=user_id,
                parameters_id=parameters_id,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # 更新任务记录
            self.all_tasks[task_id] = task
            self.task_queue.append(task)
            self.user_task_counts[user_id] = self.user_task_counts.get(user_id, 0) + 1
            
            logger.info(f"任务已提交: {task_id} (用户: {user_id})")
            return task_id

    async def cancel_task(self, user_id: uuid.UUID, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        async with self._schedule_lock:
            task = self.all_tasks.get(task_id)
            if not task or task.user_id != user_id:
                raise ValueError("任务不存在或无权访问")
            
            # 如果任务在队列中，直接移除
            if task.status == TaskStatus.PENDING or task.status == TaskStatus.QUEUED:
                try:
                    self.task_queue.remove(task)
                except ValueError:
                    pass
                task.status = TaskStatus.CANCELLED
                task.finished_at = datetime.utcnow()
                return True
                
            # 如果任务正在运行，停止任务
            elif task.status == TaskStatus.RUNNING and task.job_id:
                try:
                    if await self.finetune_service.stop_finetune(user_id, task.job_id):
                        task.status = TaskStatus.CANCELLED
                        task.finished_at = datetime.utcnow()
                        del self.running_tasks[task_id]
                        self.user_task_counts[user_id] -= 1
                        return True
                except Exception as e:
                    logger.error(f"停止任务失败 {task_id}: {str(e)}")
                    
            return False

    async def get_task_status(
        self,
        user_id: uuid.UUID,
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        task = self.all_tasks.get(task_id)
        if not task or task.user_id != user_id:
            raise ValueError("任务不存在或无权访问")
            
        status_info = {
            "task_id": task.task_id,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "finished_at": task.finished_at.isoformat() if task.finished_at else None,
            "error_message": task.error_message
        }
        
        # 如果任务正在运行，获取实时状态
        if task.status == TaskStatus.RUNNING and task.job_id:
            try:
                job_status = await self.finetune_service.get_finetune_status(
                    user_id,
                    task.job_id
                )
                status_info["job_status"] = job_status
            except Exception as e:
                logger.error(f"获取任务状态失败 {task_id}: {str(e)}")
                
        return status_info

    async def list_user_tasks(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出用户的所有任务
        
        Args:
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            任务列表
        """
        user_tasks = [
            task for task in self.all_tasks.values()
            if task.user_id == user_id
        ]
        
        # 按创建时间排序
        user_tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页
        tasks = user_tasks[skip:skip + limit]
        
        return [{
            "task_id": task.task_id,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "finished_at": task.finished_at.isoformat() if task.finished_at else None,
            "error_message": task.error_message
        } for task in tasks]

    async def _task_scheduler(self):
        """任务调度器"""
        while True:
            try:
                async with self._schedule_lock:
                    # 检查是否可以启动新任务
                    while (len(self.running_tasks) < self.max_concurrent_tasks and 
                           self.task_queue):
                        task = self.task_queue.popleft()
                        await self._start_task(task)
                        
                # 更新运行中任务的状态
                await self._update_running_tasks()
                
            except Exception as e:
                logger.error(f"任务调度器错误: {str(e)}")
                
            await asyncio.sleep(5)  # 调度间隔

    async def _start_task(self, task: FinetuneTask):
        """启动任务"""
        try:
            # 启动微调任务
            result = await self.finetune_service.start_finetune(
                task.user_id,
                task.parameters_id
            )
            
            # 更新任务信息
            task.job_id = result["job_id"]
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # 添加到运行中的任务
            self.running_tasks[task.task_id] = task
            
            logger.info(f"任务已启动: {task.task_id} (Job ID: {task.job_id})")
            
        except Exception as e:
            logger.error(f"启动任务失败 {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.finished_at = datetime.utcnow()
            self.user_task_counts[task.user_id] -= 1

    async def _update_running_tasks(self):
        """更新运行中任务的状态"""
        completed_tasks = []
        
        for task_id, task in self.running_tasks.items():
            try:
                status = await self.finetune_service.get_finetune_status(
                    task.user_id,
                    task.job_id
                )
                
                # 检查任务是否完成
                if status.get("succeeded"):
                    task.status = TaskStatus.COMPLETED
                    completed_tasks.append(task_id)
                elif status.get("failed"):
                    task.status = TaskStatus.FAILED
                    task.error_message = "任务执行失败"
                    completed_tasks.append(task_id)
                    
            except Exception as e:
                logger.error(f"更新任务状态失败 {task_id}: {str(e)}")
        
        # 清理已完成的任务
        async with self._schedule_lock:
            for task_id in completed_tasks:
                task = self.running_tasks.pop(task_id)
                task.finished_at = datetime.utcnow()
                self.user_task_counts[task.user_id] -= 1
