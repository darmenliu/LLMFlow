
class QuantizationParameters:
    def __init__(self, quantization_method: str, quantization_bits: int, prompt_template: str):
        self.quantization_method = quantization_method
        self.quantization_bits = quantization_bits
        self.prompt_template = prompt_template

class AcceleratorParameters:
    def __init__(self, accelerator_type: str, num_processes: int, rope_interpolation_type: str):
        self.rope_interpolation_type = rope_interpolation_type
        self.accelerator_type = accelerator_type


class OptimizerParameters:
    def __init__(self, learning_rate: float, weight_decay: float, betas: list[float], compute_dtype: str, num_epochs: int, batch_size: int):
        self.learning_rate = learning_rate
        self.compute_dtype = compute_dtype
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.weight_decay = weight_decay
        self.betas = betas

class LoraParameters:
    def __init__(self, lora_alpha: int, lora_r: int, scaling_factor: float, learing_rate_ratio: float, lora_dropout: float, is_create_new_adapter: bool, is_rls_lora: bool, is_do_lora: bool, is_pissa: bool, lora_target_modules: list[str]):
        self.lora_alpha = lora_alpha
        self.lora_r = lora_r
        self.scaling_factor = scaling_factor
        self.learing_rate_ratio = learing_rate_ratio
        self.lora_dropout = lora_dropout
        self.is_create_new_adapter = is_create_new_adapter
        self.is_rls_lora = is_rls_lora
        self.is_do_lora = is_do_lora
        self.is_pissa = is_pissa
        self.lora_target_modules = lora_target_modules

class FinetuneParameters:
    def __init__(self, model_name: str, dataset_name: str, finetune_method: str, training_phase: str, checkpoint_path: str, quantization_parameters: QuantizationParameters, optimizer_parameters: OptimizerParameters, accelerator_parameters: AcceleratorParameters, lora_parameters: LoraParameters):
        self.model_name = model_name
        self.finetune_method = finetune_method
        self.training_phase = training_phase
        self.checkpoint_path = checkpoint_path
        self.dataset_name = dataset_name
        self.quantization_parameters = quantization_parameters 
        self.optimizer_parameters = optimizer_parameters
        self.accelerator_parameters = accelerator_parameters
        self.lora_parameters = lora_parameters
