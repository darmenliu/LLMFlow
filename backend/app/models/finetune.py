from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class FinetuneParametersDB(SQLModel, table=True):
    __tablename__ = "finetune_parameters"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 基础参数
    model_name: str
    dataset_name: str
    finetune_method: str
    training_phase: str
    checkpoint_path: str
    
    # 量化参数
    quantization_method: str
    quantization_bits: int
    prompt_template: str
    
    # 加速器参数
    accelerator_type: str
    num_processes: int
    rope_interpolation_type: str
    
    # 优化器参数
    learning_rate: float
    weight_decay: float
    betas: str  # JSON string
    compute_dtype: str
    num_epochs: int
    batch_size: int
    
    # LoRA参数
    lora_alpha: float
    lora_r: int
    scaling_factor: float
    learing_rate_ratio: float
    lora_dropout: float
    is_create_new_adapter: bool
    is_rls_lora: bool
    is_do_lora: bool
    is_pissa: bool
    lora_target_modules: str  # JSON string
