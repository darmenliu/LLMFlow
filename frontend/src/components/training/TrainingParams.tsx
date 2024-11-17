import React from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  Select,
  Input,
  VStack,
  Radio,
  RadioGroup,
  Stack,
  HStack,
  SimpleGrid,
  Text,
  Tooltip,
  Icon,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Divider,
} from "@chakra-ui/react"
import { InfoIcon } from '@chakra-ui/icons'

export interface TrainingConfig {
  // 原有的配置
  finetuneMethod: string
  checkpointPath: string
  quantizationLevel: string
  quantizationMethod: string
  promptTemplate: string
  ropeMethod: string
  accelerationMethod: string

  // 新增的训练配置
  trainingStage: string
  dataPath: string
  dataset: string
  learningRate: number
  epochs: number
  maxGradNorm: number
  maxSamples: number
  computeType: string
  truncationLength: number
  batchSize: number
  gradientAccumulation: number
  validationSplit: number
  lrScheduler: string
}

interface TrainingParamsProps {
  onChange?: (params: TrainingConfig) => void
}

const TRAINING_STAGES = [
  { value: "sft", label: "Supervised Fine-Tuning" },
  { value: "rm", label: "Reward Modeling" },
  { value: "ppo", label: "PPO Training" },
] as const

const COMPUTE_TYPES = [
  { value: "fp32", label: "FP32" },
  { value: "fp16", label: "FP16" },
  { value: "bf16", label: "BF16" },
] as const

const LR_SCHEDULERS = [
  { value: "cosine", label: "Cosine" },
  { value: "linear", label: "Linear" },
  { value: "constant", label: "Constant" },
] as const

const FINETUNE_METHODS = [
  { value: "lora", label: "LoRA" },
  { value: "qlora", label: "QLoRA" },
  { value: "peft", label: "PEFT" },
] as const

const QUANTIZATION_LEVELS = [
  { value: "none", label: "不进行量化" },
  { value: "4bit", label: "4-bit 量化" },
  { value: "8bit", label: "8-bit 量化" },
] as const

const QUANTIZATION_METHODS = [
  { value: "bitsandbytes", label: "BitsAndBytes" },
  { value: "gptq", label: "GPTQ" },
  { value: "awq", label: "AWQ" },
] as const

const PROMPT_TEMPLATES = [
  { value: "default", label: "默认模板" },
  { value: "alpaca", label: "Alpaca" },
  { value: "vicuna", label: "Vicuna" },
  { value: "custom", label: "自定义模板" },
] as const

const ROPE_METHODS = [
  { value: "none", label: "不使用" },
  { value: "linear", label: "线性插值" },
  { value: "dynamic", label: "动态插值" },
] as const

const ACCELERATION_METHODS = [
  { value: "auto", label: "自动选择" },
  { value: "flashattn2", label: "Flash Attention 2" },
  { value: "unsloth", label: "Unsloth" },
  { value: "liger_kernel", label: "Liger Kernel" },
] as const

type SelectEvent = React.ChangeEvent<HTMLSelectElement>
type InputEvent = React.ChangeEvent<HTMLInputElement>
type RadioChangeEvent = string

const ParamLabel: React.FC<{ label: string; tooltip: string }> = ({ label, tooltip }) => (
  <HStack spacing={2}>
    <FormLabel mb={0} whiteSpace="nowrap">{label}</FormLabel>
    <Tooltip label={tooltip} placement="top">
      <Icon as={InfoIcon} color="gray.500" w={4} h={4} />
    </Tooltip>
  </HStack>
)

export default function TrainingParams({ onChange }: TrainingParamsProps) {
  const [config, setConfig] = React.useState<TrainingConfig>({
    // 原有配置的初始值
    finetuneMethod: "lora",
    checkpointPath: "",
    quantizationLevel: "none",
    quantizationMethod: "bitsandbytes",
    promptTemplate: "default",
    ropeMethod: "none",
    accelerationMethod: "auto",

    // 新增配置的初始值
    trainingStage: "sft",
    dataPath: "",
    dataset: "",
    learningRate: 5e-5,
    epochs: 3.0,
    maxGradNorm: 1.0,
    maxSamples: 100000,
    computeType: "bf16",
    truncationLength: 1024,
    batchSize: 2,
    gradientAccumulation: 4,
    validationSplit: 0.1,
    lrScheduler: "cosine",
  })

  const handleChange = <K extends keyof TrainingConfig>(
    field: K,
    value: TrainingConfig[K]
  ) => {
    const newConfig = { ...config, [field]: value }
    setConfig(newConfig)
    onChange?.(newConfig)
  }

  const handleSelectChange = (e: SelectEvent, field: keyof TrainingConfig) => {
    handleChange(field, e.target.value)
  }

  const handleInputChange = (e: InputEvent, field: keyof TrainingConfig) => {
    handleChange(field, e.target.value)
  }

  const handleNumberChange = (_: string, value: number, field: keyof TrainingConfig) => {
    handleChange(field, value)
  }

  const handleRadioChange = (value: RadioChangeEvent, field: keyof TrainingConfig) => {
    handleChange(field, value)
  }

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="sm">
      <VStack spacing={6} align="stretch">
        {/* 微调配置 */}
        <Box>
          <Text fontSize="md" fontWeight="bold" mb={4} color="green.500">微调配置</Text>
          <SimpleGrid columns={3} spacing={4}>
            <FormControl>
              <ParamLabel 
                label="微调方法" 
                tooltip="选择模型微调的具体方法" 
              />
              <Select
                value={config.finetuneMethod}
                onChange={(e) => handleSelectChange(e, "finetuneMethod")}
                size="sm"
              >
                {FINETUNE_METHODS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="训练阶段" 
                tooltip="选择模型训练的具体阶段" 
              />
              <Select
                value={config.trainingStage}
                onChange={(e) => handleSelectChange(e, "trainingStage")}
                size="sm"
              >
                {TRAINING_STAGES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="检查点路径" 
                tooltip="模型检查点的保存路径" 
              />
              <Input
                value={config.checkpointPath}
                onChange={(e) => handleInputChange(e, "checkpointPath")}
                placeholder="/path/to/checkpoint"
                size="sm"
              />
            </FormControl>
          </SimpleGrid>
        </Box>

        {/* 原有的量化配置 */}
        <Box>
          <Text fontSize="md" fontWeight="bold" mb={4} color="green.500">量化配置</Text>
          <SimpleGrid columns={3} spacing={4}>
            <FormControl>
              <ParamLabel 
                label="量化等级" 
                tooltip="选择模型量化的精度" 
              />
              <Select
                value={config.quantizationLevel}
                onChange={(e) => handleSelectChange(e, "quantizationLevel")}
                size="sm"
              >
                {QUANTIZATION_LEVELS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="量化方法" 
                tooltip="选择具体的量化算法" 
              />
              <Select
                value={config.quantizationMethod}
                onChange={(e) => handleSelectChange(e, "quantizationMethod")}
                size="sm"
                isDisabled={config.quantizationLevel === "none"}
              >
                {QUANTIZATION_METHODS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="提示模板" 
                tooltip="选择训练使用的提示词模板" 
              />
              <Select
                value={config.promptTemplate}
                onChange={(e) => handleSelectChange(e, "promptTemplate")}
                size="sm"
              >
                {PROMPT_TEMPLATES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>
          </SimpleGrid>
        </Box>

        {/* 原有的加速配置 */}
        <Box>
          <Text fontSize="md" fontWeight="bold" mb={4} color="green.500">加速配置</Text>
          <SimpleGrid columns={2} spacing={4}>
            <FormControl>
              <ParamLabel 
                label="RoPE插值" 
                tooltip="选择位置编码的插值方法" 
              />
              <RadioGroup
                value={config.ropeMethod}
                onChange={(value: RadioChangeEvent) => handleRadioChange(value, "ropeMethod")}
              >
                <Stack direction="row" spacing={4}>
                  {ROPE_METHODS.map(({ value, label }) => (
                    <Radio key={value} value={value} size="sm">{label}</Radio>
                  ))}
                </Stack>
              </RadioGroup>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="加速方式" 
                tooltip="选择训练加速方法" 
              />
              <RadioGroup
                value={config.accelerationMethod}
                onChange={(value) => handleChange("accelerationMethod", value)}
              >
                <Stack direction="row" spacing={4} wrap="wrap">
                  {ACCELERATION_METHODS.map(({ value, label }) => (
                    <Radio key={value} value={value} size="sm">{label}</Radio>
                  ))}
                </Stack>
              </RadioGroup>
            </FormControl>
          </SimpleGrid>
        </Box>

        <Divider />

        {/* 新增的优化器配置 */}
        <Box>
          <Text fontSize="md" fontWeight="bold" mb={4} color="green.500">优化器配置</Text>
          <SimpleGrid columns={2} spacing={4}>
            <FormControl>
              <ParamLabel 
                label="学习率" 
                tooltip="AdamW优化器的初始学习率" 
              />
              <NumberInput
                value={config.learningRate}
                onChange={(_, value) => handleNumberChange(_, value, "learningRate")}
                defaultValue={5e-5}
                min={1e-6}
                max={1e-2}
                precision={6}
                step={1e-6}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="训练轮数" 
                tooltip="模型训练的总轮数" 
              />
              <NumberInput
                value={config.epochs}
                onChange={(_, value) => handleNumberChange(_, value, "epochs")}
                defaultValue={3}
                min={1}
                max={100}
                precision={1}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="最大梯度范数" 
                tooltip="梯度裁剪的最大范数值" 
              />
              <NumberInput
                value={config.maxGradNorm}
                onChange={(_, value) => handleNumberChange(_, value, "maxGradNorm")}
                defaultValue={1.0}
                min={0.1}
                max={10}
                precision={1}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="计算类型" 
                tooltip="选择计算精度类型" 
              />
              <Select
                value={config.computeType}
                onChange={(e) => handleSelectChange(e, "computeType")}
                size="sm"
              >
                {COMPUTE_TYPES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>
          </SimpleGrid>
        </Box>

        {/* 新增的高级配置 */}
        <Box>
          <Text fontSize="md" fontWeight="bold" mb={4} color="green.500">高级配置</Text>
          <SimpleGrid columns={2} spacing={4}>
            <FormControl>
              <ParamLabel 
                label="截断长度" 
                tooltip="输入序列的最大长度" 
              />
              <NumberInput
                value={config.truncationLength}
                onChange={(_, value) => handleNumberChange(_, value, "truncationLength")}
                defaultValue={1024}
                min={128}
                max={4096}
                step={128}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="批处理大小" 
                tooltip="每个GPU处理的样本数量" 
              />
              <NumberInput
                value={config.batchSize}
                onChange={(_, value) => handleNumberChange(_, value, "batchSize")}
                defaultValue={2}
                min={1}
                max={32}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="梯度累积" 
                tooltip="梯度累积的步数" 
              />
              <HStack spacing={4}>
                <NumberInput
                  value={config.gradientAccumulation}
                  onChange={(_, value) => handleNumberChange(_, value, "gradientAccumulation")}
                  defaultValue={4}
                  min={1}
                  max={32}
                  size="sm"
                  flex={1}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Slider
                  value={config.gradientAccumulation}
                  onChange={(value) => handleChange("gradientAccumulation", value)}
                  min={1}
                  max={32}
                  flex={2}
                  size="sm"
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb />
                </Slider>
              </HStack>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="验证集比例" 
                tooltip="验证集占总样本的比例" 
              />
              <HStack spacing={4}>
                <NumberInput
                  value={config.validationSplit}
                  onChange={(_, value) => handleNumberChange(_, value, "validationSplit")}
                  defaultValue={0.1}
                  min={0}
                  max={0.5}
                  step={0.05}
                  precision={2}
                  size="sm"
                  flex={1}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <Slider
                  value={config.validationSplit * 100}
                  onChange={(value) => handleChange("validationSplit", value / 100)}
                  min={0}
                  max={50}
                  flex={2}
                  size="sm"
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb />
                </Slider>
              </HStack>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="学习率调节器" 
                tooltip="选择学习率的调整策略" 
              />
              <Select
                value={config.lrScheduler}
                onChange={(e) => handleSelectChange(e, "lrScheduler")}
                size="sm"
              >
                {LR_SCHEDULERS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <ParamLabel 
                label="最大样本数" 
                tooltip="每个数据集的最大样本数量" 
              />
              <NumberInput
                value={config.maxSamples}
                onChange={(_, value) => handleChange("maxSamples", value)}
                defaultValue={100000}
                min={1000}
                max={1000000}
                step={1000}
                size="sm"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
          </SimpleGrid>
        </Box>
      </VStack>
    </Box>
  )
} 