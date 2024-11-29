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

    def list_finetune_jobs(
        self,
        namespace: str,
        label_selector: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        列出指定命名空间下的微调任务
        
        Args:
            namespace: Kubernetes命名空���
            label_selector: 标签选择器，例如 "user-id=123"
            
        Returns:
            任务列表，每个任务包含完整的job信息
            
        Raises:
            Exception: 获取任务列表失败
        """
        try:
            # 获取所有带有指定标签的job
            jobs = self.kube_client.list_namespaced_job(
                namespace=namespace,
                label_selector=label_selector
            )
            
            # 转换为列表格式
            job_list = []
            for job in jobs.items:
                job_info = {
                    "job_id": job.metadata.labels.get("job-id"),
                    "name": job.metadata.name,
                    "status": {
                        "active": job.status.active,
                        "succeeded": job.status.succeeded,
                        "failed": job.status.failed,
                        "completion_time": job.status.completion_time.isoformat() if job.status.completion_time else None,
                        "start_time": job.status.start_time.isoformat() if job.status.start_time else None,
                    },
                    "metadata": {
                        "creation_timestamp": job.metadata.creation_timestamp.isoformat(),
                        "labels": job.metadata.labels,
                        "annotations": job.metadata.annotations
                    }
                }
                
                # 获取任务的额外状态信息
                try:
                    metrics = self.get_finetune_job_metrics(
                        job_id=job_info["job_id"],
                        namespace=namespace
                    )
                    job_info["metrics"] = metrics
                except Exception:
                    job_info["metrics"] = None
                    
                job_list.append(job_info)
                
            return job_list

        except Exception as e:
            logger.error(f"获取微调任务列表失败: {str(e)}")
            raise

    def get_finetune_job_logs(
        self,
        job_id: str,
        namespace: Optional[str] = None,
        tail_lines: Optional[int] = None,
        follow: bool = False
    ) -> str:
        """
        获取微调任务的日志
        
        Args:
            job_id: 任务ID
            namespace: Kubernetes命名空间
            tail_lines: 返回最后的行数，None表示返回所有日志
            follow: 是否持续跟踪日志
            
        Returns:
            任务日志内容
            
        Raises:
            Exception: 获取日志失败
        """
        try:
            namespace = namespace or self.default_namespace
            job_name = f"finetune-{job_id}"
            
            # 获取job关联的pods
            pods = self.kube_client.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"job-name={job_name}"
            )
            
            if not pods.items:
                raise ValueError(f"未找到任务 {job_id} 相关的Pod")
            
            # 获取最新的pod
            pod = sorted(
                pods.items,
                key=lambda x: x.metadata.creation_timestamp,
                reverse=True
            )[0]
            
            # 获取pod日志
            logs = self.kube_client.read_namespaced_pod_log(
                name=pod.metadata.name,
                namespace=namespace,
                tail_lines=tail_lines,
                follow=follow,
                timestamps=True  # 添加时间戳
            )
            
            return logs

        except Exception as e:
            logger.error(f"获取微调任务日志失败: {str(e)}")
            raise

    def get_finetune_job_metrics(
        self,
        job_id: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取微调任务的指标数据
        
        Args:
            job_id: 任务ID
            namespace: Kubernetes命名空间
            
        Returns:
            任务指标数据，包括训练进度、损失值等
            
        Raises:
            Exception: 获取指标失败
        """
        try:
            namespace = namespace or self.default_namespace
            job_name = f"finetune-{job_id}"
            
            # 获取job关联的pods
            pods = self.kube_client.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"job-name={job_name}"
            )
            
            if not pods.items:
                raise ValueError(f"未找到任务 {job_id} 相关的Pod")
            
            # 获取最新的pod
            pod = sorted(
                pods.items,
                key=lambda x: x.metadata.creation_timestamp,
                reverse=True
            )[0]
            
            # 从pod的注解中获取指标数据
            metrics = pod.metadata.annotations.get("finetune-metrics", "{}")
            metrics = json.loads(metrics)
            
            # 添加基本训练信息
            metrics.update({
                "pod_name": pod.metadata.name,
                "pod_status": pod.status.phase,
                "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
                "resource_usage": {
                    "cpu": pod.status.container_statuses[0].usage.get("cpu") if pod.status.container_statuses else None,
                    "memory": pod.status.container_statuses[0].usage.get("memory") if pod.status.container_statuses else None,
                    "gpu": pod.status.container_statuses[0].usage.get("nvidia.com/gpu") if pod.status.container_statuses else None
                }
            })
            
            return metrics

        except Exception as e:
            logger.error(f"获取微调任务指标失败: {str(e)}")
            raise

    def get_finetune_job(
        self,
        job_id: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取微调任务的详细信息
        
        Args:
            job_id: 任务ID
            namespace: Kubernetes命名空间
            
        Returns:
            任务的完整信息，包括元数据、状态等
            
        Raises:
            ValueError: 任务不存在
            Exception: 获取任务信息失败
        """
        try:
            namespace = namespace or self.default_namespace
            job_name = f"finetune-{job_id}"
            
            # 获取job信息
            job = self.kube_client.read_namespaced_job(
                name=job_name,
                namespace=namespace
            )
            
            # 转换为字典格式
            job_info = {
                "metadata": {
                    "name": job.metadata.name,
                    "namespace": job.metadata.namespace,
                    "creation_timestamp": job.metadata.creation_timestamp.isoformat(),
                    "labels": job.metadata.labels or {},
                    "annotations": job.metadata.annotations or {},
                    "uid": job.metadata.uid
                },
                "spec": {
                    "parallelism": job.spec.parallelism,
                    "completions": job.spec.completions,
                    "active_deadline_seconds": job.spec.active_deadline_seconds,
                    "backoff_limit": job.spec.backoff_limit,
                    "template": {
                        "spec": {
                            "containers": [{
                                "name": container.name,
                                "image": container.image,
                                "resources": {
                                    "requests": container.resources.requests,
                                    "limits": container.resources.limits
                                } if container.resources else {}
                            } for container in job.spec.template.spec.containers]
                        }
                    }
                },
                "status": {
                    "active": job.status.active,
                    "succeeded": job.status.succeeded,
                    "failed": job.status.failed,
                    "completion_time": job.status.completion_time.isoformat() if job.status.completion_time else None,
                    "start_time": job.status.start_time.isoformat() if job.status.start_time else None,
                    "conditions": [{
                        "type": condition.type,
                        "status": condition.status,
                        "last_probe_time": condition.last_probe_time.isoformat() if condition.last_probe_time else None,
                        "last_transition_time": condition.last_transition_time.isoformat() if condition.last_transition_time else None,
                        "reason": condition.reason,
                        "message": condition.message
                    } for condition in (job.status.conditions or [])]
                }
            }
            
            # 获取关联的pods信息
            pods = self.kube_client.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"job-name={job_name}"
            )
            
            job_info["pods"] = [{
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
                "container_statuses": [{
                    "name": status.name,
                    "ready": status.ready,
                    "restart_count": status.restart_count,
                    "state": {
                        "running": {
                            "started_at": status.state.running.started_at.isoformat()
                        } if status.state.running else None,
                        "terminated": {
                            "exit_code": status.state.terminated.exit_code,
                            "reason": status.state.terminated.reason,
                            "message": status.state.terminated.message,
                            "started_at": status.state.terminated.started_at.isoformat() if status.state.terminated.started_at else None,
                            "finished_at": status.state.terminated.finished_at.isoformat() if status.state.terminated.finished_at else None
                        } if status.state.terminated else None,
                        "waiting": {
                            "reason": status.state.waiting.reason,
                            "message": status.state.waiting.message
                        } if status.state.waiting else None
                    }
                } for status in (pod.status.container_statuses or [])]
            } for pod in pods.items]
            
            return job_info

        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                raise ValueError(f"未找到任务: {job_id}")
            raise
        except Exception as e:
            logger.error(f"获取微调任务信息失败: {str(e)}")
            raise
