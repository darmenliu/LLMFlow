from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.core.taskmanager.finetune_task_manager import FinetuneTaskManager
from app.core.finetune.finetune_parameters import (
    FinetuneParameters,
    QuantizationParameters,
    AcceleratorParameters,
    OptimizerParameters,
    LoraParameters
)
from app.core.finetune.finetune_crud import FinetuneParametersCRUD
from app.core.taskmanager.task_manager_singleton import get_task_manager

router = APIRouter()

logger = logging.getLogger(__name__)

class StartFinetuneRequest(BaseModel):
    """微调任务启动请求"""
    # 基础参数
    model_name: str = Field(..., description="模型名称")
    dataset_name: str = Field(..., description="数据集名称")
    finetune_method: str = Field(..., description="微调方法")
    training_phase: str = Field(..., description="训练阶段")
    checkpoint_path: Optional[str] = Field(None, description="检查点路径")
    
    # 量化参数
    quantization_method: str = Field(..., description="量化方法")
    quantization_bits: int = Field(..., description="量化位数")
    prompt_template: str = Field(..., description="提示模板")
    
    # 加速器参数
    accelerator_type: str = Field(..., description="加速器类型")
    rope_interpolation_type: str = Field(..., description="RoPE插值类型")
    
    # 优化器参数
    learning_rate: float = Field(..., description="学习率")
    weight_decay: float = Field(0.01, description="权重衰减")
    betas: List[float] = Field([0.9, 0.999], description="Adam优化器参数")
    compute_dtype: str = Field(..., description="计算数据类型")
    num_epochs: int = Field(..., description="训练轮数")
    batch_size: int = Field(..., description="批次大小")
    
    # LoRA参数
    lora_alpha: int = Field(16, description="LoRA alpha参数")
    lora_r: int = Field(8, description="LoRA rank")
    scaling_factor: float = Field(1.0, description="缩放因子")
    learing_rate_ratio: float = Field(1.0, description="学习率比例")
    lora_dropout: float = Field(0.05, description="LoRA dropout")
    is_create_new_adapter: bool = Field(True, description="是否创建新adapter")
    is_rls_lora: bool = Field(False, description="是否使用RLS-LoRA")
    is_do_lora: bool = Field(True, description="是否使用LoRA")
    is_pissa: bool = Field(False, description="是否使用PISSA")
    lora_target_modules: List[str] = Field(..., description="LoRA目标模块")
    
    class Config:
        schema_extra = {
            "example": {
                "model_name": "llama2-7b",
                "dataset_name": "alpaca-zh",
                "finetune_method": "lora",
                "training_phase": "training",
                "quantization_method": "int4",
                "quantization_bits": 4,
                "prompt_template": "default",
                "accelerator_type": "cuda",
                "rope_interpolation_type": "linear",
                "learning_rate": 3e-4,
                "compute_dtype": "float16",
                "num_epochs": 3,
                "batch_size": 4,
                "lora_target_modules": ["q_proj", "v_proj"]
            }
        }
    
class StartFinetuneResponse(BaseModel):
    """微调任务启动响应"""
    task_id: str
    message: str
    status: Dict[str, Any]


@router.post("/start", response_model=StartFinetuneResponse)
async def start_finetune(
    request: StartFinetuneRequest,
    session: SessionDep,
    current_user: CurrentUser,
    task_manager: FinetuneTaskManager = Depends(get_task_manager)
) -> Any:
    """
    启动微调任务
    
    Args:
        request: 启动请求参数
        session: 数据库会话
        current_user: 当前用户
        task_manager: 任务管理器
        
    Returns:
        包含任务ID和状态的响应
        
    Raises:
        HTTPException: 启动失败时抛出异常
    """
    # try:
    logger.info(f"启动微调任务: {request}")
    # 构建调参数
    finetune_parameters = FinetuneParameters(
        model_name=request.model_name,
        dataset_name=request.dataset_name,
        finetune_method=request.finetune_method,
        training_phase=request.training_phase,
        checkpoint_path=request.checkpoint_path,
        
        quantization_parameters=QuantizationParameters(
            quantization_method=request.quantization_method,
            quantization_bits=request.quantization_bits,
            prompt_template=request.prompt_template
        ),
        
        accelerator_parameters=AcceleratorParameters(
            accelerator_type=request.accelerator_type,
            rope_interpolation_type=request.rope_interpolation_type
        ),
        
        optimizer_parameters=OptimizerParameters(
            learning_rate=request.learning_rate,
            weight_decay=request.weight_decay,
            betas=request.betas,
            compute_dtype=request.compute_dtype,
            num_epochs=request.num_epochs,
            batch_size=request.batch_size
        ),
        
        lora_parameters=LoraParameters(
            lora_alpha=request.lora_alpha,
            lora_r=request.lora_r,
            scaling_factor=request.scaling_factor,
            learing_rate_ratio=request.learing_rate_ratio,
            lora_dropout=request.lora_dropout,
            is_create_new_adapter=request.is_create_new_adapter,
            is_rls_lora=request.is_rls_lora,
            is_do_lora=request.is_do_lora,
            is_pissa=request.is_pissa,
            lora_target_modules=request.lora_target_modules
        )
    )
    logger.info(f"微调参数: {finetune_parameters}")
    # 保存微调参数
    parameters_db = FinetuneParametersCRUD.create_parameters(
        session=session,
        user_id=current_user.id,
        name=f"{request.model_name}-{request.finetune_method}",
        parameters=finetune_parameters,
        description=f"为{request.model_name}模型使用{request.finetune_method}方法进行微调"
    )
    logger.info(f"微调参数已保存: {parameters_db.id}")
    # 提交任务到任务管理器
    task_id = await task_manager.submit_task(
        user_id=current_user.id,
        parameters_id=parameters_db.id
    )
    logger.info(f"微调任务已提交: {task_id}")
    # 获取任务状态
    status = await task_manager.get_task_status(
        user_id=current_user.id,
        task_id=task_id
    )
    logger.info(f"微调任务状态: {status}") 
    return StartFinetuneResponse(
        task_id=task_id,
        message="微调任务已成功提交",
        status=status
    )
    
    # except ValueError as e:
    #     # 处理参数验证错误
    #     logger.error(f"参数验证错误: {str(e)}")
    #     raise HTTPException(
    #         status_code=400,
    #         detail=str(e)
    #     )
    # except Exception as e:
    #     # 处理其他错误
    #     logger.error(f"启动微调任务失败: {str(e)}")
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"启动微调任务失败: {str(e)}"
    #     )

@router.post("/stop/{task_id}", response_model=Message)
async def stop_finetune(
    task_id: str,
    current_user: CurrentUser,
    task_manager: FinetuneTaskManager = Depends(get_task_manager)
) -> Any:
    """
    停止微调任务
    
    Args:
        task_id: 任务ID
        current_user: 当前用户
        task_manager: 任务管理器
        
    Returns:
        停止结果消息
        
    Raises:
        HTTPException: 停止失败时抛出异常
    """
    try:
        # 尝试停止任务
        result = await task_manager.cancel_task(
            user_id=current_user.id,
            task_id=task_id
        )
        logger.info(f"停止微调任务: {result}")
        if result:
            return Message(message=f"微调任务 {task_id} 已成功停止")
        else:
            raise HTTPException(
                status_code=400,
                detail="无法停止任务，可能任务已完成或已停止"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"停止任务失败: {str(e)}"
        )

@router.get("/status/{task_id}")
async def get_finetune_status(
    task_id: str,
    current_user: CurrentUser,
    task_manager: FinetuneTaskManager = Depends(get_task_manager)
) -> Dict[str, Any]:
    """
    获取微调任务状态
    
    Args:
        task_id: 任务ID
        current_user: 当前用户
        task_manager: 任务管理器
        
    Returns:
        任务状态信息，包括：
        - 基本状态（pending/running/completed等）
        - 创建时间
        - 开始时间
        - 完成时间
        - 错误信息（如果有）
        - K8s任务状态（如果正在运行）
        
    Raises:
        HTTPException: 获取状态失败时抛出异常
    """
    try:
        # 获取任务状态
        status = await task_manager.get_task_status(
            user_id=current_user.id,
            task_id=task_id
        )
        
        # 如果任务正在运行，尝试获取训练指标
        if status.get("status") == "running" and status.get("job_status"):
            try:
                metrics = await task_manager.finetune_service.get_finetune_metrics(
                    user_id=current_user.id,
                    job_id=status["job_status"].get("job_id")
                )
                status["metrics"] = metrics
            except Exception as e:
                logger.warning(f"获取训练指标失败: {str(e)}")
                
        return status
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取任务状态失败: {str(e)}"
        )
