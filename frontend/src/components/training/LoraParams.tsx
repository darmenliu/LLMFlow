import React from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  VStack,
  HStack,
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
  Checkbox,
  Input,
  SimpleGrid,
} from "@chakra-ui/react"
import { InfoIcon } from '@chakra-ui/icons'

export interface LoraConfig {
  rank: number
  alpha: number
  dropout: number
  learningRateScale: number
  createNewAdapter: boolean
  enableRsLora: boolean
  enableDora: boolean
  enablePiSSA: boolean
  targetModules: string
  additionalModules: string
}

interface LoraParamsProps {
  onChange?: (config: LoraConfig) => void
}

const ParamLabel: React.FC<{ label: string; tooltip: string }> = ({ label, tooltip }) => (
  <HStack spacing={2}>
    <FormLabel mb={0} whiteSpace="nowrap" color="green.500">{label}</FormLabel>
    <Tooltip label={tooltip} placement="top">
      <Icon as={InfoIcon} color="green.500" w={4} h={4} />
    </Tooltip>
  </HStack>
)

export default function LoraParams({ onChange }: LoraParamsProps) {
  const [config, setConfig] = React.useState<LoraConfig>({
    rank: 8,
    alpha: 16,
    dropout: 0,
    learningRateScale: 0,
    createNewAdapter: false,
    enableRsLora: false,
    enableDora: false,
    enablePiSSA: false,
    targetModules: "",
    additionalModules: "",
  })

  const handleChange = <K extends keyof LoraConfig>(
    field: K,
    value: LoraConfig[K]
  ) => {
    const newConfig = { ...config, [field]: value }
    setConfig(newConfig)
    onChange?.(newConfig)
  }

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="sm">
      <VStack spacing={4} align="stretch">
        {/* 数值参数设置 - 两行布局 */}
        <SimpleGrid columns={2} spacing={4}>
          {/* 第一行：LoRA秩和缩放系数 */}
          <FormControl>
            <ParamLabel 
              label="LoRA 秩" 
              tooltip="设置LoRA矩阵的秩大小，较大的值会增加模型参数量" 
            />
            <HStack spacing={2}>
              <NumberInput
                value={config.rank}
                onChange={(_, val) => handleChange("rank", Number(val))}
                min={1}
                max={64}
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
                value={config.rank}
                onChange={(value) => handleChange("rank", value)}
                min={1}
                max={64}
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
              label="缩放系数" 
              tooltip="设置LoRA的缩放系数，影响LoRA权重的作用强度" 
            />
            <HStack spacing={2}>
              <NumberInput
                value={config.alpha}
                onChange={(_, val) => handleChange("alpha", Number(val))}
                min={1}
                max={128}
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
                value={config.alpha}
                onChange={(value) => handleChange("alpha", value)}
                min={1}
                max={128}
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

          {/* 第二行：随机丢弃和学习率比例 */}
          <FormControl>
            <ParamLabel 
              label="随机丢弃" 
              tooltip="设置LoRA权重的随机丢弃概率，用于防止过拟合" 
            />
            <HStack spacing={2}>
              <NumberInput
                value={config.dropout}
                onChange={(_, val) => handleChange("dropout", Number(val))}
                min={0}
                max={1}
                step={0.01}
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
                value={config.dropout}
                onChange={(value) => handleChange("dropout", value)}
                min={0}
                max={1}
                step={0.01}
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
              label="学习率比例" 
              tooltip="设置LoRA+ B矩阵的学习率倍率" 
            />
            <HStack spacing={2}>
              <NumberInput
                value={config.learningRateScale}
                onChange={(_, val) => handleChange("learningRateScale", Number(val))}
                min={0}
                max={10}
                step={0.1}
                precision={1}
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
                value={config.learningRateScale}
                onChange={(value) => handleChange("learningRateScale", value)}
                min={0}
                max={10}
                step={0.1}
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
        </SimpleGrid>

        {/* 复选框选项 - 一行四列布局 */}
        <SimpleGrid columns={4} spacing={4}>
          <FormControl>
            <Checkbox
              isChecked={config.createNewAdapter}
              onChange={(e) => handleChange("createNewAdapter", e.target.checked)}
              colorScheme="green"
            >
              <Text color="green.500" fontSize="sm">创建新适配器</Text>
            </Checkbox>
          </FormControl>

          <FormControl>
            <Checkbox
              isChecked={config.enableRsLora}
              onChange={(e) => handleChange("enableRsLora", e.target.checked)}
              colorScheme="green"
            >
              <Text color="green.500" fontSize="sm">启用 rsLoRA</Text>
            </Checkbox>
          </FormControl>

          <FormControl>
            <Checkbox
              isChecked={config.enableDora}
              onChange={(e) => handleChange("enableDora", e.target.checked)}
              colorScheme="green"
            >
              <Text color="green.500" fontSize="sm">启用 DoRA</Text>
            </Checkbox>
          </FormControl>

          <FormControl>
            <Checkbox
              isChecked={config.enablePiSSA}
              onChange={(e) => handleChange("enablePiSSA", e.target.checked)}
              colorScheme="green"
            >
              <Text color="green.500" fontSize="sm">启用 PiSSA</Text>
            </Checkbox>
          </FormControl>
        </SimpleGrid>

        {/* 文本输入 - 两列布局 */}
        <SimpleGrid columns={2} spacing={4}>
          <FormControl>
            <ParamLabel 
              label="LoRA作用模块" 
              tooltip="输入需要应用LoRA的模块名称，多个模块用英文逗号分隔" 
            />
            <Input
              value={config.targetModules}
              onChange={(e) => handleChange("targetModules", e.target.value)}
              placeholder="例如: q_proj,v_proj,k_proj"
              size="sm"
            />
          </FormControl>

          <FormControl>
            <ParamLabel 
              label="附加模块" 
              tooltip="输入除LoRA层以外的可训练模块名称" 
            />
            <Input
              value={config.additionalModules}
              onChange={(e) => handleChange("additionalModules", e.target.value)}
              placeholder="例如: norm,bias"
              size="sm"
            />
          </FormControl>
        </SimpleGrid>
      </VStack>
    </Box>
  )
} 