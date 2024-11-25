from typing import Optional, Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KubeJobClient:
    def __init__(self, config_file: Optional[str] = None, context: Optional[str] = None):
        """
        初始化 Kubernetes 客户端
        
        Args:
            config_file: kubeconfig 文件路径，默认使用默认配置
            context: Kubernetes context 名称
        """
        try:
            if config_file:
                config.load_kube_config(config_file=config_file, context=context)
            else:
                # 尝试集群内配置，如果失败则使用默认配置
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=context)
                    
            self.batch_v1 = client.BatchV1Api()
            self.core_v1 = client.CoreV1Api()
        except Exception as e:
            logger.error(f"初始化 Kubernetes 客户端失败: {str(e)}")
            raise

    def create_job(
        self,
        name: str,
        namespace: str,
        container_image: str,
        command: list[str],
        env_vars: Optional[Dict[str, str]] = None,
        cpu_request: str = "100m",
        memory_request: str = "128Mi",
        cpu_limit: str = "1000m",
        memory_limit: str = "1Gi",
        restart_policy: str = "Never",
        backoff_limit: int = 3,
        active_deadline_seconds: int = 3600,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        service_account_name: Optional[str] = None,
        image_pull_secrets: Optional[list[str]] = None,
        volumes: Optional[list[Dict[str, Any]]] = None,
        volume_mounts: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        创建 Kubernetes Job
        
        Args:
            name: Job 名称
            namespace: 命名空间
            container_image: 容器镜像
            command: 容器命令
            env_vars: 环境变量
            cpu_request: CPU 请求
            memory_request: 内存请求
            cpu_limit: CPU 限制
            memory_limit: 内存限制
            restart_policy: 重启策略
            backoff_limit: 重试次数
            active_deadline_seconds: 任务超时时间（秒）
            labels: 标签
            annotations: 注解
            service_account_name: 服务账号名称
            image_pull_secrets: 镜像拉取密钥
            volumes: 卷配置
            volume_mounts: 卷挂载配置
        
        Returns:
            创建的 Job 信息
        """
        try:
            # 构建容器环境变量
            env = []
            if env_vars:
                env = [
                    client.V1EnvVar(name=k, value=v)
                    for k, v in env_vars.items()
                ]

            # 构建容器资源请求和限制
            resources = client.V1ResourceRequirements(
                requests={
                    "cpu": cpu_request,
                    "memory": memory_request
                },
                limits={
                    "cpu": cpu_limit,
                    "memory": memory_limit
                }
            )

            # 构建容器定义
            container = client.V1Container(
                name=name,
                image=container_image,
                command=command,
                env=env,
                resources=resources,
                volume_mounts=volume_mounts if volume_mounts else None
            )

            # 构建 Pod 模板
            pod_template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels=labels if labels else {},
                    annotations=annotations if annotations else {}
                ),
                spec=client.V1PodSpec(
                    containers=[container],
                    restart_policy=restart_policy,
                    service_account_name=service_account_name,
                    image_pull_secrets=[
                        client.V1LocalObjectReference(name=secret)
                        for secret in (image_pull_secrets or [])
                    ],
                    volumes=volumes if volumes else None
                )
            )

            # 构建 Job 定义
            job = client.V1Job(
                api_version="batch/v1",
                kind="Job",
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels if labels else {},
                    annotations=annotations if annotations else {}
                ),
                spec=client.V1JobSpec(
                    template=pod_template,
                    backoff_limit=backoff_limit,
                    active_deadline_seconds=active_deadline_seconds
                )
            )

            # 创建 Job
            api_response = self.batch_v1.create_namespaced_job(
                namespace=namespace,
                body=job
            )
            
            return self._serialize_job(api_response)

        except ApiException as e:
            logger.error(f"创建 Job 失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"创建 Job 时发生错误: {str(e)}")
            raise

    def delete_job(
        self,
        name: str,
        namespace: str,
        delete_pods: bool = True
    ) -> bool:
        """
        删除 Kubernetes Job
        
        Args:
            name: Job 名称
            namespace: 命名空间
            delete_pods: 是否同时删除相关的 Pod
            
        Returns:
            是否删除成功
        """
        try:
            # 如果需要删除相关的 Pod
            if delete_pods:
                # 获取 Job 关联的 Pod
                pods = self.core_v1.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=f"job-name={name}"
                )
                
                # 删除关联的 Pod
                for pod in pods.items:
                    self.core_v1.delete_namespaced_pod(
                        name=pod.metadata.name,
                        namespace=namespace
                    )

            # 删除 Job
            self.batch_v1.delete_namespaced_job(
                name=name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy="Background"
                )
            )
            
            return True

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Job {name} 在命名空间 {namespace} 中不存在")
                return False
            logger.error(f"删除 Job 失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"删除 Job 时发生错误: {str(e)}")
            raise

    def get_job_status(
        self,
        name: str,
        namespace: str
    ) -> Dict[str, Any]:
        """
        获取 Job 状态
        
        Args:
            name: Job 名称
            namespace: 命名空间
            
        Returns:
            Job 状态信息
        """
        try:
            job = self.batch_v1.read_namespaced_job(
                name=name,
                namespace=namespace
            )
            
            return self._serialize_job(job)

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Job {name} 在命名空间 {namespace} 中不存在")
                return {"status": "NotFound"}
            logger.error(f"获取 Job 状态失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"获取 Job 状态时发生错误: {str(e)}")
            raise

    def _serialize_job(self, job: client.V1Job) -> Dict[str, Any]:
        """
        序列化 Job 信息
        
        Args:
            job: Kubernetes Job 对象
            
        Returns:
            序列化后的 Job 信息
        """
        status = {
            "name": job.metadata.name,
            "namespace": job.metadata.namespace,
            "creation_time": job.metadata.creation_timestamp.isoformat() if job.metadata.creation_timestamp else None,
            "status": {
                "active": job.status.active if job.status.active else 0,
                "succeeded": job.status.succeeded if job.status.succeeded else 0,
                "failed": job.status.failed if job.status.failed else 0,
                "completion_time": job.status.completion_time.isoformat() if job.status.completion_time else None,
                "start_time": job.status.start_time.isoformat() if job.status.start_time else None,
            },
            "conditions": []
        }

        if job.status.conditions:
            for condition in job.status.conditions:
                status["conditions"].append({
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_transition_time": condition.last_transition_time.isoformat() if condition.last_transition_time else None
                })

        return status
