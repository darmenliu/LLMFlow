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
  Divider,
  Text,
  Tooltip,
  Icon,
  HStack,
  SimpleGrid,
} from "@chakra-ui/react"
import { InfoIcon } from '@chakra-ui/icons'

export interface TrainingConfig {
  finetuneMethod: string
  checkpointPath: string
  quantizationLevel: string
  quantizationMethod: string
  promptTemplate: string
  ropeMethod: string
  accelerationMethod: string
}

interface TrainingParamsProps {
  onChange?: (params: TrainingConfig) => void
}

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
    finetuneMethod: "lora",
    checkpointPath: "",
    quantizationLevel: "none",
    quantizationMethod: "bitsandbytes",
    promptTemplate: "default",
    ropeMethod: "none",
    accelerationMethod: "auto",
  })

  const handleChange = (field: keyof TrainingConfig, value: string) => {
    const newConfig = { ...config, [field]: value }
    setConfig(newConfig)
    onChange?.(newConfig)
  }

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="sm">
      <VStack spacing={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold" mb={4}>
          训练参数配置
        </Text>

        <SimpleGrid columns={2} spacing={4}>
          <FormControl>
            <ParamLabel 
              label="微调方法" 
              tooltip="选择模型微调的具体方法，不同方法会影响训练效果和资源消耗" 
            />
            <Select
              value={config.finetuneMethod}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
                handleChange("finetuneMethod", e.target.value)
              }
            >
              {FINETUNE_METHODS.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </Select>
          </FormControl>

          <FormControl>
            <ParamLabel 
              label="检查点路径" 
              tooltip="模型检查点的保存路径，用于断点续训或模型保存" 
            />
            <Input
              value={config.checkpointPath}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                handleChange("checkpointPath", e.target.value)
              }
              placeholder="/path/to/checkpoint"
            />
          </FormControl>
        </SimpleGrid>

        <Divider />

        <SimpleGrid columns={3} spacing={4}>
          <FormControl>
            <ParamLabel 
              label="量化等级" 
              tooltip="选择模型量化的精度，较低的精度可以减少内存占用，但可能影响模型性能" 
            />
            <Select
              value={config.quantizationLevel}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
                handleChange("quantizationLevel", e.target.value)
              }
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
              tooltip="选择具体的量化算法，不同算法在速度和精度上有所权衡" 
            />
            <Select
              value={config.quantizationMethod}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
                handleChange("quantizationMethod", e.target.value)
              }
              isDisabled={config.quantizationLevel === "none"}
              size="sm"
            >
              {QUANTIZATION_METHODS.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </Select>
          </FormControl>

          <FormControl>
            <ParamLabel 
              label="提示模板" 
              tooltip="选择用于训练的提示词模板，影响模型对输入的理解方式" 
            />
            <Select
              value={config.promptTemplate}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
                handleChange("promptTemplate", e.target.value)
              }
              size="sm"
            >
              {PROMPT_TEMPLATES.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </Select>
          </FormControl>
        </SimpleGrid>

        <SimpleGrid columns={2} spacing={4}>
          <FormControl>
            <ParamLabel 
              label="RoPE 插值方法" 
              tooltip="选择位置编码的插值方法，影响模型处理长序列的能力" 
            />
            <RadioGroup
              value={config.ropeMethod}
              onChange={(value: string) => handleChange("ropeMethod", value)}
              size="sm"
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
              tooltip="选择训练过程中使用的加速方法，影响训练速度和资源利用" 
            />
            <RadioGroup
              value={config.accelerationMethod}
              onChange={(value: string) => handleChange("accelerationMethod", value)}
              size="sm"
            >
              <Stack direction="row" spacing={4} wrap="wrap">
                {ACCELERATION_METHODS.map(({ value, label }) => (
                  <Radio key={value} value={value} size="sm">{label}</Radio>
                ))}
              </Stack>
            </RadioGroup>
          </FormControl>
        </SimpleGrid>
      </VStack>
    </Box>
  )
} 