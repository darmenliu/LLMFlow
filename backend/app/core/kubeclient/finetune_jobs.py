from typing import Optional, Dict, Any
import uuid
import json
import logging
from datetime import datetime

from app.core.kubeclient.kube_jobs import KubeJobClient
from app.core.finetune.finetune_parameters import FinetuneParameters

logger = logging.getLogger(__name__)

class FinetuneJobClient:
    def __init__(self, 
                 config_file: Optional[str] = None, 
                 context: Optional[str] = None,
                 finetune_image: str = "your-finetune-image:latest",
                 default_namespace: str = "finetune"):
        """
        微调任务客户端
        
        Args:
            config_file: kubeconfig 文件路径
            context: Kubernetes context 名称
            finetune_image: 微调任务使用的容器镜像
            default_namespace: 默认命名空间
        """
        self.kube_client = KubeJobClient(config_file, context)
        self.finetune_image = finetune_image
        self.default_namespace = default_namespace

    def create_finetune_job(
        self,
        job_id: str,
        parameters: FinetuneParameters,
        namespace: Optional[str] = None,
        cpu_request: str = "4000m",
        memory_request: str = "16Gi",
        cpu_limit: str = "8000m",
        memory_limit: str = "32Gi",
        gpu_request: Optional[str] = "1",
        active_deadline_seconds: int = 86400,  # 24小时
        service_account_name: Optional[str] = "finetune-sa",
    ) -> Dict[str, Any]:
        """
        创建微调任务
        
        Args:
            job_id: 任务ID
            parameters: 微调参数
            namespace: 命名空间
            cpu_request: CPU 请求
            memory_request: 内存请求
            cpu_limit: CPU 限制
            memory_limit: 内存限制
            gpu_request: GPU 请求数量
            active_deadline_seconds: 任务超时时间（秒）
            service_account_name: 服务账号名称
            
        Returns:
            创建的 Job 信息
        """
        try:
            # 使用提供的命名空间或默认命名空间
            namespace = namespace or self.default_namespace
            
            # 构建环境变量
            env_vars = {
                "MODEL_NAME": parameters.model_name,
                "DATASET_NAME": parameters.dataset_name,
                "FINETUNE_METHOD": parameters.finetune_method,
                "TRAINING_PHASE": parameters.training_phase,
                "CHECKPOINT_PATH": parameters.checkpoint_path,
                
                # 量化参数
                "QUANTIZATION_METHOD": parameters.quantization_parameters.quantization_method,
                "QUANTIZATION_BITS": str(parameters.quantization_parameters.quantization_bits),
                "PROMPT_TEMPLATE": parameters.quantization_parameters.prompt_template,
                
                # 加速器参数
                "ACCELERATOR_TYPE": parameters.accelerator_parameters.accelerator_type,
                "NUM_PROCESSES": str(parameters.accelerator_parameters.num_processes),
                "ROPE_INTERPOLATION_TYPE": parameters.accelerator_parameters.rope_interpolation_type,
                
                # 优化器参数
                "LEARNING_RATE": str(parameters.optimizer_parameters.learning_rate),
                "WEIGHT_DECAY": str(parameters.optimizer_parameters.weight_decay),
                "BETAS": json.dumps(parameters.optimizer_parameters.betas),
                "COMPUTE_DTYPE": parameters.optimizer_parameters.compute_dtype,
                "NUM_EPOCHS": str(parameters.optimizer_parameters.num_epochs),
                "BATCH_SIZE": str(parameters.optimizer_parameters.batch_size),
                
                # LoRA参数
                "LORA_ALPHA": str(parameters.lora_parameters.lora_alpha),
                "LORA_R": str(parameters.lora_parameters.lora_r),
                "SCALING_FACTOR": str(parameters.lora_parameters.scaling_factor),
                "LEARNING_RATE_RATIO": str(parameters.lora_parameters.learing_rate_ratio),
                "LORA_DROPOUT": str(parameters.lora_parameters.lora_dropout),
                "IS_CREATE_NEW_ADAPTER": str(parameters.lora_parameters.is_create_new_adapter),
                "IS_RLS_LORA": str(parameters.lora_parameters.is_rls_lora),
                "IS_DO_LORA": str(parameters.lora_parameters.is_do_lora),
                "IS_PISSA": str(parameters.lora_parameters.is_pissa),
                "LORA_TARGET_MODULES": json.dumps(parameters.lora_parameters.lora_target_modules)
            }

            # 构建资源配置
            resources = {}
            if gpu_request:
                resources["nvidia.com/gpu"] = gpu_request

            # 构建标签
            labels = {
                "app": "finetune",
                "job-id": job_id,
                "model": parameters.model_name,
                "type": parameters.finetune_method
            }

            # 构建注解
            annotations = {
                "finetune.ai/parameters": json.dumps({
                    "model_name": parameters.model_name,
                    "dataset_name": parameters.dataset_name,
                    "finetune_method": parameters.finetune_method,
                    "training_phase": parameters.training_phase
                })
            }

            # 创建 Job
            return self.kube_client.create_job(
                name=f"finetune-{job_id}",
                namespace=namespace,
                container_image=self.finetune_image,
                command=["python", "/app/finetune.py"],  # 假设入口点是 finetune.py
                env_vars=env_vars,
                cpu_request=cpu_request,
                memory_request=memory_request,
                cpu_limit=cpu_limit,
                memory_limit=memory_limit,
                labels=labels,
                annotations=annotations,
                service_account_name=service_account_name,
                active_deadline_seconds=active_deadline_seconds,
                # 可以根据需要添加 volumes 和 volume_mounts
            )

        except Exception as e:
            logger.error(f"创建微调任务失败: {str(e)}")
            raise

    def get_finetune_job_status(
        self,
        job_id: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取微调任务状态
        
        Args:
            job_id: 任务ID
            namespace: 命名空间
            
        Returns:
            任务状态信息
        """
        namespace = namespace or self.default_namespace
        return self.kube_client.get_job_status(
            name=f"finetune-{job_id}",
            namespace=namespace
        )

    def delete_finetune_job(
        self,
        job_id: str,
        namespace: Optional[str] = None,
        delete_pods: bool = True
    ) -> bool:
        """
        删除微调任务
        
        Args:
            job_id: 任务ID
            namespace: 命名空间
            delete_pods: 是否同时删除相关的 Pod
            
        Returns:
            是否删除成功
        """
        namespace = namespace or self.default_namespace
        return self.kube_client.delete_job(
            name=f"finetune-{job_id}",
            namespace=namespace,
            delete_pods=delete_pods
        )
