import { Box, Container, Text, VStack, Button } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import useAuth from "../../hooks/useAuth"
import ModelSelector from "../../components/training/ModelSelector"
import TrainingParams, { TrainingConfig } from "../../components/training/TrainingParams"
import DatasetSelector from "../../components/training/DatasetSelector"
import LoraParams, { LoraConfig } from "../../components/training/LoraParams"

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

  const handleStartTraining = () => {
    if (!selectedModel || !trainingConfig || !selectedDataset || !loraConfig) {
      return
    }

    console.log("开始训练:", {
      model: selectedModel,
      config: trainingConfig,
      dataset: selectedDataset,
      lora: loraConfig
    })
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

          {/* 开始训练按钮 */}
          {selectedModel && trainingConfig && selectedDataset && loraConfig && (
            <Box>
              <Button
                colorScheme="green"
                size="lg"
                width="full"
                onClick={handleStartTraining}
              >
                开始训练
              </Button>
            </Box>
          )}
        </VStack>
      </Box>
    </Container>
  )
}
