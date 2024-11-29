from typing import List, Optional
import uuid
import json
from datetime import datetime
from venv import logger
from sqlmodel import Session, select

from app.finetunedb.finetune import FinetuneParametersDB
from app.core.finetune.finetune_parameters import (
    FinetuneParameters,
    QuantizationParameters,
    AcceleratorParameters,
    OptimizerParameters,
    LoraParameters
)

class FinetuneParametersCRUD:
    @staticmethod
    def create_parameters(
        session: Session,
        user_id: uuid.UUID,
        name: str,
        parameters: FinetuneParameters,
        description: Optional[str] = None,
    ) -> FinetuneParametersDB:
        """
        创建并存储微调参数
        """
        logger.info(f"创建微调参数: {parameters}") 
        db_parameters = FinetuneParametersDB(
            user_id=user_id,
            name=name,
            description=description,
            
            # 基础参数
            model_name=parameters.model_name,
            dataset_name=parameters.dataset_name,
            finetune_method=parameters.finetune_method,
            training_phase=parameters.training_phase,
            checkpoint_path=parameters.checkpoint_path,
            
            # 量化参数
            quantization_method=parameters.quantization_parameters.quantization_method,
            quantization_bits=parameters.quantization_parameters.quantization_bits,
            prompt_template=parameters.quantization_parameters.prompt_template,
            
            # 加速器参数
            accelerator_type=parameters.accelerator_parameters.accelerator_type,
            rope_interpolation_type=parameters.accelerator_parameters.rope_interpolation_type,
            
            # 优化器参数
            learning_rate=parameters.optimizer_parameters.learning_rate,
            weight_decay=parameters.optimizer_parameters.weight_decay,
            betas=json.dumps(parameters.optimizer_parameters.betas),
            compute_dtype=parameters.optimizer_parameters.compute_dtype,
            num_epochs=parameters.optimizer_parameters.num_epochs,
            batch_size=parameters.optimizer_parameters.batch_size,
            
            # LoRA参数
            lora_alpha=parameters.lora_parameters.lora_alpha,
            lora_r=parameters.lora_parameters.lora_r,
            scaling_factor=parameters.lora_parameters.scaling_factor,
            learing_rate_ratio=parameters.lora_parameters.learing_rate_ratio,
            lora_dropout=parameters.lora_parameters.lora_dropout,
            is_create_new_adapter=parameters.lora_parameters.is_create_new_adapter,
            is_rls_lora=parameters.lora_parameters.is_rls_lora,
            is_do_lora=parameters.lora_parameters.is_do_lora,
            is_pissa=parameters.lora_parameters.is_pissa,
            lora_target_modules=json.dumps(parameters.lora_parameters.lora_target_modules)
        )
        logger.info(f"微调参数已保存: {db_parameters.id}")
        session.add(db_parameters)
        logger.info(f"提交微调参数: {db_parameters}")
        session.commit()
        logger.info(f"刷新微调参数: {db_parameters}")
        session.refresh(db_parameters)
        logger.info(f"返回微调参数: {db_parameters}")
        return db_parameters

    @staticmethod
    def get_parameters_by_id(
        session: Session,
        parameter_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[FinetuneParameters]:
        """
        根据ID获取微调参数
        """
        db_parameters = session.get(FinetuneParametersDB, parameter_id)
        
        if not db_parameters or db_parameters.user_id != user_id:
            return None
            
        return FinetuneParametersCRUD._convert_to_parameters(db_parameters)

    @staticmethod
    def list_parameters(
        session: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinetuneParametersDB]:
        """
        获取用户的所有微调参数列表
        """
        statement = select(FinetuneParametersDB).where(
            FinetuneParametersDB.user_id == user_id
        ).offset(skip).limit(limit)
        
        return session.exec(statement).all()

    @staticmethod
    def delete_parameters(
        session: Session,
        parameter_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        删除指定的微调参数
        """
        db_parameters = session.get(FinetuneParametersDB, parameter_id)
        if not db_parameters or db_parameters.user_id != user_id:
            return False
            
        session.delete(db_parameters)
        session.commit()
        return True

    @staticmethod
    def update_parameters(
        session: Session,
        parameter_id: uuid.UUID,
        user_id: uuid.UUID,
        parameters: FinetuneParameters,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[FinetuneParametersDB]:
        """
        更新微调参数
        """
        db_parameters = session.get(FinetuneParametersDB, parameter_id)
        if not db_parameters or db_parameters.user_id != user_id:
            return None
            
        # 更新基本信息
        if name is not None:
            db_parameters.name = name
        if description is not None:
            db_parameters.description = description
            
        # 更新参数
        db_parameters.model_name = parameters.model_name
        db_parameters.dataset_name = parameters.dataset_name
        db_parameters.finetune_method = parameters.finetune_method
        db_parameters.training_phase = parameters.training_phase
        db_parameters.checkpoint_path = parameters.checkpoint_path
        
        # 更新量化参数
        db_parameters.quantization_method = parameters.quantization_parameters.quantization_method
        db_parameters.quantization_bits = parameters.quantization_parameters.quantization_bits
        db_parameters.prompt_template = parameters.quantization_parameters.prompt_template
        
        # 更新加速器参数
        db_parameters.accelerator_type = parameters.accelerator_parameters.accelerator_type
        db_parameters.rope_interpolation_type = parameters.accelerator_parameters.rope_interpolation_type
        
        # 更新优化器参数
        db_parameters.learning_rate = parameters.optimizer_parameters.learning_rate
        db_parameters.weight_decay = parameters.optimizer_parameters.weight_decay
        db_parameters.betas = json.dumps(parameters.optimizer_parameters.betas)
        db_parameters.compute_dtype = parameters.optimizer_parameters.compute_dtype
        db_parameters.num_epochs = parameters.optimizer_parameters.num_epochs
        db_parameters.batch_size = parameters.optimizer_parameters.batch_size
        
        # 更新LoRA参数
        db_parameters.lora_alpha = parameters.lora_parameters.lora_alpha
        db_parameters.lora_r = parameters.lora_parameters.lora_r
        db_parameters.scaling_factor = parameters.lora_parameters.scaling_factor
        db_parameters.learing_rate_ratio = parameters.lora_parameters.learing_rate_ratio
        db_parameters.lora_dropout = parameters.lora_parameters.lora_dropout
        db_parameters.is_create_new_adapter = parameters.lora_parameters.is_create_new_adapter
        db_parameters.is_rls_lora = parameters.lora_parameters.is_rls_lora
        db_parameters.is_do_lora = parameters.lora_parameters.is_do_lora
        db_parameters.is_pissa = parameters.lora_parameters.is_pissa
        db_parameters.lora_target_modules = json.dumps(parameters.lora_parameters.lora_target_modules)
        
        db_parameters.updated_at = datetime.utcnow()
        
        session.add(db_parameters)
        session.commit()
        session.refresh(db_parameters)
        
        return db_parameters

    @staticmethod
    def _convert_to_parameters(db_parameters: FinetuneParametersDB) -> FinetuneParameters:
        """
        将数据库模型转换为FinetuneParameters对象
        """
        quantization_parameters = QuantizationParameters(
            quantization_method=db_parameters.quantization_method,
            quantization_bits=db_parameters.quantization_bits,
            prompt_template=db_parameters.prompt_template
        )
        
        accelerator_parameters = AcceleratorParameters(
            accelerator_type=db_parameters.accelerator_type,
            rope_interpolation_type=db_parameters.rope_interpolation_type
        )
        
        optimizer_parameters = OptimizerParameters(
            learning_rate=db_parameters.learning_rate,
            weight_decay=db_parameters.weight_decay,
            betas=json.loads(db_parameters.betas),
            compute_dtype=db_parameters.compute_dtype,
            num_epochs=db_parameters.num_epochs,
            batch_size=db_parameters.batch_size
        )
        
        lora_parameters = LoraParameters(
            lora_alpha=db_parameters.lora_alpha,
            lora_r=db_parameters.lora_r,
            scaling_factor=db_parameters.scaling_factor,
            learing_rate_ratio=db_parameters.learing_rate_ratio,
            lora_dropout=db_parameters.lora_dropout,
            is_create_new_adapter=db_parameters.is_create_new_adapter,
            is_rls_lora=db_parameters.is_rls_lora,
            is_do_lora=db_parameters.is_do_lora,
            is_pissa=db_parameters.is_pissa,
            lora_target_modules=json.loads(db_parameters.lora_target_modules)
        )
        
        return FinetuneParameters(
            model_name=db_parameters.model_name,
            dataset_name=db_parameters.dataset_name,
            finetune_method=db_parameters.finetune_method,
            training_phase=db_parameters.training_phase,
            checkpoint_path=db_parameters.checkpoint_path,
            quantization_parameters=quantization_parameters,
            optimizer_parameters=optimizer_parameters,
            accelerator_parameters=accelerator_parameters,
            lora_parameters=lora_parameters
        ) 
