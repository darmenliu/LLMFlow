from typing import Optional, List, Dict, Any
from enum import Enum

class ModelType(str, Enum):
    """模型类型枚举"""
    ORIGINAL = "original"      # 原始模型
    FINETUNED = "finetuned"   # 微调模型
    QUANTIZED = "quantized"    # 量化模型
    MERGED = "merged"         # 合并模型

class ModelStatus(str, Enum):
    """模型状态枚举"""
    DRAFT = "draft"           # 草稿
    UPLOADING = "uploading"   # 上传中
    UPLOADED = "uploaded"     # 已上传
    PROCESSING = "processing" # 处理中
    READY = "ready"          # 就绪
    DEPLOYED = "deployed"    # 已部署
    FAILED = "failed"        # 失败
    ARCHIVED = "archived"    # 已归档

class ModelFormat(str, Enum):
    """模型格式枚举"""
    PYTORCH = "pytorch"       # .pt, .pth
    ONNX = "onnx"           # .onnx
    SAFETENSORS = "safetensors" # .safetensors
    BINARY = "binary"       # .bin

class QuantizationType(str, Enum):
    """量化类型枚举"""
    INT4 = "int4"
    INT8 = "int8"
    FP16 = "fp16"
    NONE = "none"

class ModelMetrics:
    """模型评估指标"""
    def __init__(
        self,
        accuracy: float = 0.0,
        loss: float = 0.0,
        perplexity: Optional[float] = None,
        latency: Optional[float] = None,
        throughput: Optional[float] = None,
        memory_usage: Optional[int] = None,
        custom_metrics: Optional[Dict[str, Any]] = None
    ):
        self.accuracy = accuracy
        self.loss = loss
        self.perplexity = perplexity
        self.latency = latency          # 延迟（毫秒）
        self.throughput = throughput    # 吞吐量（tokens/s）
        self.memory_usage = memory_usage # 内存使用（MB）
        self.custom_metrics = custom_metrics or {}

class ModelConfig:
    """模型配置"""
    def __init__(
        self,
        model_type: str,
        model_family: str,
        model_size: str,
        vocab_size: int,
        max_sequence_length: int,
        hidden_size: int,
        num_attention_heads: int,
        num_hidden_layers: int,
        intermediate_size: int,
        quantization_config: Optional[Dict[str, Any]] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ):
        self.model_type = model_type
        self.model_family = model_family
        self.model_size = model_size
        self.vocab_size = vocab_size
        self.max_sequence_length = max_sequence_length
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.num_hidden_layers = num_hidden_layers
        self.intermediate_size = intermediate_size
        self.quantization_config = quantization_config or {}
        self.custom_config = custom_config or {}

class ModelFile:
    """模型文件信息"""
    def __init__(
        self,
        filename: str,
        file_size: int,
        file_format: ModelFormat,
        checksum: str,
        file_path: str,
        upload_time: str,
        is_compressed: bool = False,
        compression_format: Optional[str] = None
    ):
        self.filename = filename
        self.file_size = file_size
        self.file_format = file_format
        self.checksum = checksum
        self.file_path = file_path
        self.upload_time = upload_time
        self.is_compressed = is_compressed
        self.compression_format = compression_format

class LLMModel:
    """LLM模型完整信息"""
    def __init__(
        self,
        id: str,
        name: str,
        version: str,
        description: Optional[str],
        model_type: ModelType,
        status: ModelStatus,
        created_by: str,
        created_at: str,
        updated_at: str,
        model_config: ModelConfig,
        model_files: List[ModelFile],
        metrics: Optional[ModelMetrics] = None,
        parent_model_id: Optional[str] = None,
        tags: List[str] = None,
        deployment_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.model_type = model_type
        self.status = status
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at
        self.model_config = model_config
        self.model_files = model_files
        self.metrics = metrics or ModelMetrics()
        self.parent_model_id = parent_model_id
        self.tags = tags or []
        self.deployment_config = deployment_config or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "model_type": self.model_type.value,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model_config": {
                "model_type": self.model_config.model_type,
                "model_family": self.model_config.model_family,
                "model_size": self.model_config.model_size,
                "vocab_size": self.model_config.vocab_size,
                "max_sequence_length": self.model_config.max_sequence_length,
                "hidden_size": self.model_config.hidden_size,
                "num_attention_heads": self.model_config.num_attention_heads,
                "num_hidden_layers": self.model_config.num_hidden_layers,
                "intermediate_size": self.model_config.intermediate_size,
                "quantization_config": self.model_config.quantization_config,
                "custom_config": self.model_config.custom_config
            },
            "model_files": [
                {
                    "filename": f.filename,
                    "file_size": f.file_size,
                    "file_format": f.file_format.value,
                    "checksum": f.checksum,
                    "file_path": f.file_path,
                    "upload_time": f.upload_time,
                    "is_compressed": f.is_compressed,
                    "compression_format": f.compression_format
                }
                for f in self.model_files
            ],
            "metrics": {
                "accuracy": self.metrics.accuracy,
                "loss": self.metrics.loss,
                "perplexity": self.metrics.perplexity,
                "latency": self.metrics.latency,
                "throughput": self.metrics.throughput,
                "memory_usage": self.metrics.memory_usage,
                "custom_metrics": self.metrics.custom_metrics
            },
            "parent_model_id": self.parent_model_id,
            "tags": self.tags,
            "deployment_config": self.deployment_config,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMModel':
        """从字典创建模型实例"""
        model_config = ModelConfig(
            model_type=data["model_config"]["model_type"],
            model_family=data["model_config"]["model_family"],
            model_size=data["model_config"]["model_size"],
            vocab_size=data["model_config"]["vocab_size"],
            max_sequence_length=data["model_config"]["max_sequence_length"],
            hidden_size=data["model_config"]["hidden_size"],
            num_attention_heads=data["model_config"]["num_attention_heads"],
            num_hidden_layers=data["model_config"]["num_hidden_layers"],
            intermediate_size=data["model_config"]["intermediate_size"],
            quantization_config=data["model_config"].get("quantization_config"),
            custom_config=data["model_config"].get("custom_config")
        )

        model_files = [
            ModelFile(
                filename=f["filename"],
                file_size=f["file_size"],
                file_format=ModelFormat(f["file_format"]),
                checksum=f["checksum"],
                file_path=f["file_path"],
                upload_time=f["upload_time"],
                is_compressed=f.get("is_compressed", False),
                compression_format=f.get("compression_format")
            )
            for f in data["model_files"]
        ]

        metrics = ModelMetrics(
            accuracy=data["metrics"]["accuracy"],
            loss=data["metrics"]["loss"],
            perplexity=data["metrics"].get("perplexity"),
            latency=data["metrics"].get("latency"),
            throughput=data["metrics"].get("throughput"),
            memory_usage=data["metrics"].get("memory_usage"),
            custom_metrics=data["metrics"].get("custom_metrics")
        )

        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            model_type=ModelType(data["model_type"]),
            status=ModelStatus(data["status"]),
            created_by=data["created_by"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            model_config=model_config,
            model_files=model_files,
            metrics=metrics,
            parent_model_id=data.get("parent_model_id"),
            tags=data.get("tags", []),
            deployment_config=data.get("deployment_config"),
            metadata=data.get("metadata")
        )
