import { Box, Container, Text, VStack, Button, SimpleGrid, FormControl, FormLabel, Input, useToast } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import useAuth from "../../hooks/useAuth"
import ModelSelector from "../../components/training/ModelSelector"
import TrainingParams, { TrainingConfig } from "../../components/training/TrainingParams"
import DatasetSelector from "../../components/training/DatasetSelector"
import LoraParams, { LoraConfig } from "../../components/training/LoraParams"
import { DownloadIcon, ArrowUpIcon } from "@chakra-ui/icons"
import { FinetuneService, type TDataStartFinetune } from "../../client/services"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

interface SelectedModel {
  type: "online" | "local" | "existing"
  modelId?: string
  file?: File
  localPath?: string
}

interface SelectedDataset {
  type: "online" | "local" | "upload"
  datasetId?: string
  file?: File
  localPath?: string
}

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [selectedModel, setSelectedModel] = useState<SelectedModel | null>(null)
  const [trainingConfig, setTrainingConfig] = useState<TrainingConfig | null>(null)
  const [selectedDataset, setSelectedDataset] = useState<SelectedDataset | null>(null)
  const [loraConfig, setLoraConfig] = useState<LoraConfig | null>(null)
  const [isTraining, setIsTraining] = useState(false)
  const toast = useToast()

  const handleModelSelect = (modelInfo: SelectedModel) => {
    setSelectedModel(modelInfo)
    switch (modelInfo.type) {
      case "online":
        console.log(`选择了在线模型: ${modelInfo.modelId}`)
        break
      case "existing":
        console.log(`选择了已有模型: ${modelInfo.modelId}，路径: ${modelInfo.localPath}`)
        break
      case "local":
        console.log(`上传了本地模型: ${modelInfo.file?.name}`)
        break
    }
  }

  const handleTrainingConfigChange = (config: TrainingConfig) => {
    setTrainingConfig(config)
    console.log("训练配置已更新:", config)
  }

  const handleDatasetSelect = (datasetInfo: SelectedDataset) => {
    setSelectedDataset(datasetInfo)
    switch (datasetInfo.type) {
      case "online":
        console.log(`选择了在线数据集: ${datasetInfo.datasetId}`)
        break
      case "local":
        console.log(`选择了本地数据集: ${datasetInfo.datasetId}，路径: ${datasetInfo.localPath}`)
        break
      case "upload":
        console.log(`上传了新数据集: ${datasetInfo.file?.name}`)
        break
    }
  }

  const handleLoraConfigChange = (config: LoraConfig) => {
    setLoraConfig(config)
    console.log("LoRA配置已更新:", config)
  }

  const handleStartTraining = async () => {
    if (!selectedModel || !selectedDataset || !trainingConfig || !loraConfig) {
      toast({
        title: "参数错误",
        description: "请确保已选择模型、数据集，并完成所有配置",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
      return
    }

    try {
      setIsTraining(true)
      
      // 获取模型和数据集名称
      let modelName = ""
      let datasetName = ""

      switch (selectedModel.type) {
        case "online":
          modelName = selectedModel.modelId ?? ""
          break
        case "existing":
          modelName = selectedModel.localPath ?? ""
          break
        case "local":
          modelName = selectedModel.file?.name ?? ""
          break
      }

      switch (selectedDataset.type) {
        case "online":
          datasetName = selectedDataset.datasetId ?? ""
          break
        case "local":
          datasetName = selectedDataset.localPath ?? ""
          break
        case "upload":
          datasetName = selectedDataset.file?.name ?? ""
          break
      }

      if (!modelName || !datasetName) {
        throw new Error("模型或数据集名称无效")
      }
      
      // 准备请求数据
      const requestBody: TDataStartFinetune = {
        model_name: modelName,
        dataset_name: datasetName,
        finetune_method: trainingConfig.finetuneMethod,
        training_phase: trainingConfig.trainingStage,
        checkpoint_path: trainingConfig.checkpointPath,
        
        // 量化参数
        quantization_method: trainingConfig.quantizationMethod,
        quantization_bits: trainingConfig.quantizationLevel === "4bit" ? 4 : 8,
        prompt_template: trainingConfig.promptTemplate,
        
        // 加速器参数
        accelerator_type: trainingConfig.accelerationMethod,
        rope_interpolation_type: trainingConfig.ropeMethod,
        
        // 优化器参数
        learning_rate: trainingConfig.learningRate,
        weight_decay: 0.01,
        betas: [0.9, 0.999],
        compute_dtype: trainingConfig.computeType,
        num_epochs: trainingConfig.epochs,
        batch_size: trainingConfig.batchSize,
        
        // LoRA参数
        lora_alpha: loraConfig.alpha,
        lora_r: loraConfig.rank,
        scaling_factor: 1.0,
        learing_rate_ratio: loraConfig.learningRateScale,
        lora_dropout: loraConfig.dropout,
        is_create_new_adapter: loraConfig.createNewAdapter,
        is_rls_lora: loraConfig.enableRsLora,
        is_do_lora: loraConfig.enableDora,
        is_pissa: loraConfig.enablePiSSA,
        lora_target_modules: loraConfig.targetModules.split(",").map((s: string) => s.trim()).filter(Boolean)
      }

      // 调用微调服务
      const result = await FinetuneService.startFinetune({ requestBody })
      
      toast({
        title: "训练任务已提交",
        description: result.message,
        status: "success",
        duration: 5000,
        isClosable: true,
      })
      
    } catch (error) {
      toast({
        title: "启动训练失败",
        description: error instanceof Error ? error.message : "未知错误",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsTraining(false)
    }
  }

  const handleStopTraining = () => {
    setIsTraining(false)
    console.log("中断训练")
  }

  const handleSaveConfig = () => {
    if (!selectedModel || !trainingConfig || !selectedDataset || !loraConfig) {
      return
    }

    const config = {
      model: selectedModel,
      training: trainingConfig,
      dataset: selectedDataset,
      lora: loraConfig,
      timestamp: new Date().toISOString(),
    }

    // 将配置转换为字符串
    const configString = JSON.stringify(config, null, 2)
    
    // 创建 Blob
    const blob = new Blob([configString], { type: 'application/json' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `training-config-${new Date().toISOString().slice(0,10)}.json`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleLoadConfig = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const config = JSON.parse(e.target?.result as string)
        setSelectedModel(config.model)
        setTrainingConfig(config.training)
        setSelectedDataset(config.dataset)
        setLoraConfig(config.lora)
      } catch (error) {
        console.error('配置文件解析失败:', error)
      }
    }
    reader.readAsText(file)
  }

  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <VStack spacing={8} align="stretch">
          <Text fontSize="2xl" color="green.500">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text mb={6} color="green.500">欢迎使用模型微调平台</Text>
          
          {/* 第一步：模型选择区域 */}
          <Box>
            <Text fontSize="xl" fontWeight="bold" mb={4} color="green.500">
              第一步：选择或上传模型
            </Text>
            <ModelSelector onModelSelect={handleModelSelect} />
          </Box>

          {/* 显示已选择的模型信息 */}
          {selectedModel && (
            <Box mt={4} p={4} borderWidth={1} borderRadius="lg" bg="gray.50">
              <Text fontWeight="bold" color="green.500">已选择的模型：</Text>
              <Text color="green.500">
                {(() => {
                  switch (selectedModel.type) {
                    case "online":
                      return `在线模型 - ${selectedModel.modelId}`
                    case "existing":
                      return `本地已有模型 - ${selectedModel.modelId}`
                    case "local":
                      return `上传的模型 - ${selectedModel.file?.name}`
                  }
                })()}
              </Text>
            </Box>
          )}

          {/* 第二步：训练参数配置区域 */}
          <Box>
            <Text fontSize="xl" fontWeight="bold" mb={4} color="green.500">
              第二步：配置训练参数
            </Text>
            <TrainingParams onChange={handleTrainingConfigChange} />
          </Box>

          {/* 第三步：数据集选择区域 */}
          <Box>
            <Text fontSize="xl" fontWeight="bold" mb={4} color="green.500">
              第三步：选择训练数据集
            </Text>
            <DatasetSelector onDatasetSelect={handleDatasetSelect} />
          </Box>

          {/* 显示已选择的数据集信息 */}
          {selectedDataset && (
            <Box mt={4} p={4} borderWidth={1} borderRadius="lg" bg="gray.50">
              <Text fontWeight="bold" color="green.500">已选择的数据集：</Text>
              <Text color="green.500">
                {(() => {
                  switch (selectedDataset.type) {
                    case "online":
                      return `在线数据集 - ${selectedDataset.datasetId}`
                    case "local":
                      return `本地数据集 - ${selectedDataset.datasetId}`
                    case "upload":
                      return `上传的数据集 - ${selectedDataset.file?.name}`
                  }
                })()}
              </Text>
            </Box>
          )}

          {/* 第四步：LoRA参数设置 */}
          <Box>
            <Text fontSize="xl" fontWeight="bold" mb={4} color="green.500">
              第四步：配置 LoRA 参数
            </Text>
            <LoraParams onChange={handleLoraConfigChange} />
          </Box>

          {/* 训练控制按钮 */}
          <SimpleGrid columns={2} spacing={4}>
            <Button
              colorScheme="green"
              size="lg"
              width="full"
              onClick={handleStartTraining}
              isDisabled={!selectedModel || !selectedDataset || isTraining}
              isLoading={isTraining}
              loadingText="训练中..."
            >
              开始训练
            </Button>
            <Button
              colorScheme="red"
              size="lg"
              width="full"
              onClick={handleStopTraining}
              isDisabled={!isTraining}
              variant="outline"
            >
              中断训练
            </Button>
          </SimpleGrid>

          {/* 配置保存和载入按钮 */}
          <SimpleGrid columns={2} spacing={4}>
            <Button
              colorScheme="blue"
              size="md"
              width="full"
              onClick={handleSaveConfig}
              isDisabled={!selectedModel || !trainingConfig || !selectedDataset || !loraConfig}
              leftIcon={<DownloadIcon />}
              variant="outline"
            >
              保存训练参数
            </Button>
            <FormControl>
              <FormLabel htmlFor="config-file" margin={0}>
                <Button
                  as="span"
                  colorScheme="blue"
                  size="md"
                  width="full"
                  leftIcon={<ArrowUpIcon />}
                  variant="outline"
                >
                  载入训练参数
                </Button>
              </FormLabel>
              <Input
                id="config-file"
                type="file"
                accept=".json"
                onChange={handleLoadConfig}
                display="none"
              />
            </FormControl>
          </SimpleGrid>
        </VStack>
      </Box>
    </Container>
  )
}
