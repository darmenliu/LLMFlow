from typing import Optional, Dict, Any
import uuid
import logging
from datetime import datetime

from app.core.finetune.finetune import FinetuneInterface
from app.core.finetune.finetune_parameters import FinetuneParameters
from app.core.kubeclient.finetune_jobs import FinetuneJobClient
from app.core.finetune.finetune_crud import FinetuneParametersCRUD
from sqlmodel import Session

logger = logging.getLogger(__name__)

class K8sFinetuneService(FinetuneInterface):
    """
    基于 Kubernetes Job 的微调服务实现
    """
    
    def __init__(
        self,
        finetune_job_client: FinetuneJobClient,
        db_session: Session,
        namespace: str = "finetune"
    ):
        """
        初始化K8s微调服务
        
        Args:
            finetune_job_client: Kubernetes任务客户端
            db_session: 数据库会话
            namespace: Kubernetes命名空间
        """
        self.job_client = finetune_job_client
        self.db_session = db_session
        self.namespace = namespace

    async def start_finetune(
        self,
        user_id: uuid.UUID,
        parameters_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """启动微调任务"""
        # try:
        # 获取微调参数
        parameters = FinetuneParametersCRUD.get_parameters_by_id(
            self.db_session, 
            parameters_id, 
            user_id
        )
        if not parameters:
            raise ValueError(f"未找到微调参数: {parameters_id}")

        # 生成任务ID
        job_id = str(uuid.uuid4())

        # 创建微调任务
        job_info = self.job_client.create_finetune_job(
            job_id=job_id,
            parameters=parameters,
            namespace=self.namespace
        )

        logger.info(f"成功启动微调任务: {job_id}")
        return {
            "job_id": job_id,
            "status": job_info
        }

        # except Exception as e:
        #     logger.error(f"启动微调任务失败: {str(e)}")
        #     raise

    async def stop_finetune(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> bool:
        """停止微调任务"""
        try:
            # 验证任务归属
            if not await self._verify_job_ownership(user_id, job_id):
                raise ValueError("无权访问该任务")

            result = self.job_client.delete_finetune_job(
                job_id=job_id,
                namespace=self.namespace
            )
            
            if result:
                logger.info(f"成功停止微调任务: {job_id}")
            else:
                logger.warning(f"停止微调任务失败: {job_id}")
                
            return result

        except Exception as e:
            logger.error(f"停止微调任务时发生错误: {str(e)}")
            raise

    async def get_finetune_status(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> Dict[str, Any]:
        """获取微调任务状态"""
        try:
            # 验证任务归属
            if not await self._verify_job_ownership(user_id, job_id):
                raise ValueError("无权访问该任务")

            status = self.job_client.get_finetune_job_status(
                job_id=job_id,
                namespace=self.namespace
            )
            return status

        except Exception as e:
            logger.error(f"获取微调任务状态失败: {str(e)}")
            raise

    async def list_finetune_jobs(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """列出用户的微调任务"""
        try:
            # 获取用户的所有任务
            jobs = self.job_client.list_finetune_jobs(
                namespace=self.namespace,
                label_selector=f"user-id={str(user_id)}"
            )
            
            # 分页处理
            total = len(jobs)
            jobs = jobs[skip:skip + limit]
            
            return {
                "total": total,
                "jobs": jobs
            }

        except Exception as e:
            logger.error(f"获取微调任务列表失败: {str(e)}")
            raise

    async def get_finetune_logs(
        self,
        user_id: uuid.UUID,
        job_id: str,
        tail_lines: Optional[int] = None
    ) -> str:
        """获取微调任务的日志"""
        try:
            # 验证任务归属
            if not await self._verify_job_ownership(user_id, job_id):
                raise ValueError("无权访问该任务")

            logs = self.job_client.get_finetune_job_logs(
                job_id=job_id,
                namespace=self.namespace,
                tail_lines=tail_lines
            )
            return logs

        except Exception as e:
            logger.error(f"获取微调任务日志失败: {str(e)}")
            raise

    async def get_finetune_metrics(
        self,
        user_id: uuid.UUID,
        job_id: str,
    ) -> Dict[str, Any]:
        """获取微调任务的指标"""
        try:
            # 验证任务归属
            if not await self._verify_job_ownership(user_id, job_id):
                raise ValueError("无权访问该任务")

            metrics = self.job_client.get_finetune_job_metrics(
                job_id=job_id,
                namespace=self.namespace
            )
            return metrics

        except Exception as e:
            logger.error(f"获取微调任务指标失败: {str(e)}")
            raise

    async def _verify_job_ownership(self, user_id: uuid.UUID, job_id: str) -> bool:
        """
        验证任务是否属于指定用户
        
        Args:
            user_id: 用户ID
            job_id: 任务ID
            
        Returns:
            是否属于该用户
        """
        try:
            job_info = self.job_client.get_finetune_job(
                job_id=job_id,
                namespace=self.namespace
            )
            return job_info.get("metadata", {}).get("labels", {}).get("user-id") == str(user_id)
            
        except Exception:
            return False
