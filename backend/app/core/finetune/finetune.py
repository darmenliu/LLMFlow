from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid

class FinetuneInterface(ABC):
    """
    微调服务的抽象接口
    """
    
    @abstractmethod
    async def start_finetune(
        self,
        user_id: uuid.UUID,
        parameters_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        启动微调任务
        
        Args:
            user_id: 用户ID
            parameters_id: 微调参数ID
            
        Returns:
            任务信息，包含job_id和状态
            
        Raises:
            ValueError: 参数无效或未找到
            Exception: 创建任务失败
        """
        pass

    @abstractmethod
    async def stop_finetune(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> bool:
        """
        停止微调任务
        
        Args:
            user_id: 用户ID
            job_id: 任务ID
        Returns:
            是否成功停止任务
            
        Raises:
            Exception: 停止任务失败
        """
        pass

    @abstractmethod
    async def get_finetune_status(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        获取微调任务状态
        
        Args:
            user_id: 用户ID
            job_id: 任务ID
            
        Returns:
            任务状态信息
            
        Raises:
            Exception: 获取状态失败
        """
        pass

    @abstractmethod
    async def list_finetune_jobs(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """
        列出用户的微调任务
        
        Args:
            user_id: 用户ID
            namespace: 运行命名空间
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            任务列表
            
        Raises:
            Exception: 获取任务列表失败
        """
        pass

    @abstractmethod
    async def get_finetune_logs(
        self,
        user_id: uuid.UUID,
        job_id: str,
        tail_lines: Optional[int] = None
    ) -> str:
        """
        获取微调任务的日志
        
        Args:
            user_id: 用户ID
            job_id: 任务ID
            tail_lines: 返回最后的行数
            
        Returns:
            任务日志内容
            
        Raises:
            Exception: 获取日志失败
        """
        pass

    @abstractmethod
    async def get_finetune_metrics(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        获取微调任务的指标
        
        Args:
            user_id: 用户ID
            job_id: 任务ID
            
        Returns:
            任务指标数据
            
        Raises:
            Exception: 获取指标失败
        """
        pass
