import { Box, Container, Text, VStack } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import useAuth from "../../hooks/useAuth"
import ModelSelector from "../../components/training/ModelSelector"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

interface SelectedModel {
  type: "online" | "local" | "existing"
  modelId?: string
  file?: File
  localPath?: string
}

function Dashboard() {
  const { user: currentUser } = useAuth()
  const [selectedModel, setSelectedModel] = useState<SelectedModel | null>(null)

  const handleModelSelect = (modelInfo: SelectedModel) => {
    setSelectedModel(modelInfo)
    // 可以在这里添加其他处理逻辑，比如：
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

  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <VStack spacing={6} align="stretch">
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text mb={6}>欢迎使用模型微调平台</Text>

          {/* 模型选择区域 */}
          <Box>
            <Text fontSize="xl" fontWeight="bold" mb={4}>
              第一步：选择或上传模型
            </Text>
            <ModelSelector onModelSelect={handleModelSelect} />
          </Box>

          {/* 这里可以根据selectedModel的状态显示下一步操作 */}
          {selectedModel && (
            <Box mt={4} p={4} borderWidth={1} borderRadius="lg" bg="gray.50">
              <Text fontWeight="bold">已选择的模型：</Text>
              <Text>
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
        </VStack>
      </Box>
    </Container>
  )
}
