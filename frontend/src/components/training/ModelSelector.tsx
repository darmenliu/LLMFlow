import React, { useState, useEffect } from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  Select,
  Radio,
  RadioGroup,
  Stack,
  Input,
  VStack,
  Text,
  Progress,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from "@chakra-ui/react"

interface ModelOption {
  id: string
  name: string
  description: string
  size: string
}

interface LocalModelOption {
  id: string
  name: string
  path: string
  size: string
  lastModified: string
  format: string
}

const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: "gpt2-small",
    name: "GPT-2 Small",
    description: "适用于一般文本生成任务",
    size: "124M"
  },
  {
    id: "bert-base",
    name: "BERT Base Chinese",
    description: "适用于中文NLP任务",
    size: "392M"
  },
  {
    id: "t5-small",
    name: "T5 Small",
    description: "适用于文本转换任务",
    size: "242M"
  },
]

// 模拟本地已存在的模型列表
const LOCAL_MODELS: LocalModelOption[] = [
  {
    id: "local-gpt2",
    name: "本地GPT2微调模型",
    path: "/models/gpt2-finetune-v1",
    size: "1.2GB",
    lastModified: "2024-03-20",
    format: "safetensors"
  },
  {
    id: "local-bert",
    name: "中文BERT分类模型",
    path: "/models/bert-chinese-cls",
    size: "385MB",
    lastModified: "2024-03-18",
    format: "bin"
  },
]

interface ModelSelectorProps {
  onModelSelect?: (modelInfo: {
    type: "online" | "local" | "existing"
    modelId?: string
    file?: File
    localPath?: string
  }) => void
}

export default function ModelSelector({ onModelSelect }: ModelSelectorProps) {
  const [sourceType, setSourceType] = useState<"online" | "local">("online")
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [localModelInfo, setLocalModelInfo] = useState<File | null>(null)
  const [selectedLocalModel, setSelectedLocalModel] = useState<string>("")
  const [localModelTab, setLocalModelTab] = useState<number>(0)
  const toast = useToast()
  
  const handleModelFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 2 * 1024 * 1024 * 1024) {
        toast({
          title: "文件过大",
          description: "模型文件不能超过2GB",
          status: "error",
          duration: 3000,
        })
        return
      }

      setLocalModelInfo(file)
      let progress = 0
      const interval = setInterval(() => {
        progress += 5
        setUploadProgress(progress)
        if (progress >= 100) {
          clearInterval(interval)
          toast({
            title: "模型文件已就绪",
            description: `${file.name} 已准备完成`,
            status: "success",
            duration: 3000,
          })
        }
      }, 100)
    }
  }

  useEffect(() => {
    if (sourceType === "online" && selectedModel) {
      onModelSelect?.({
        type: "online",
        modelId: selectedModel
      })
    } else if (sourceType === "local") {
      if (localModelTab === 0 && selectedLocalModel) {
        const model = LOCAL_MODELS.find(m => m.id === selectedLocalModel)
        onModelSelect?.({
          type: "existing",
          modelId: selectedLocalModel,
          localPath: model?.path
        })
      } else if (localModelTab === 1 && localModelInfo && uploadProgress === 100) {
        onModelSelect?.({
          type: "local",
          file: localModelInfo
        })
      }
    }
  }, [sourceType, selectedModel, localModelInfo, uploadProgress, selectedLocalModel, localModelTab])

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="sm">
      <VStack spacing={6} align="stretch">
        <FormControl>
          <FormLabel fontWeight="bold">模型来源</FormLabel>
          <RadioGroup value={sourceType} onChange={(value: "online" | "local") => {
            setSourceType(value)
            setSelectedModel("")
            setLocalModelInfo(null)
            setUploadProgress(0)
            setSelectedLocalModel("")
          }}>
            <Stack direction="row" spacing={5}>
              <Radio value="online">使用在线模型</Radio>
              <Radio value="local">使用本地模型</Radio>
            </Stack>
          </RadioGroup>
        </FormControl>

        {sourceType === "online" ? (
          <FormControl>
            <FormLabel fontWeight="bold">选择预训练模型</FormLabel>
            <Select
              placeholder="请选择一个模型"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {AVAILABLE_MODELS.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name} ({model.size})
                </option>
              ))}
            </Select>
            {selectedModel && (
              <Text mt={2} fontSize="sm" color="gray.600">
                {AVAILABLE_MODELS.find(m => m.id === selectedModel)?.description}
              </Text>
            )}
          </FormControl>
        ) : (
          <Box>
            <Tabs variant="enclosed" onChange={(index) => setLocalModelTab(index)}>
              <TabList>
                <Tab>选择已有模型</Tab>
                <Tab>上传新模型</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <FormControl>
                    <FormLabel fontWeight="bold">选择本地模型</FormLabel>
                    <Select
                      placeholder="请选择已有的模型"
                      value={selectedLocalModel}
                      onChange={(e) => setSelectedLocalModel(e.target.value)}
                    >
                      {LOCAL_MODELS.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </Select>
                    {selectedLocalModel && (
                      <Box mt={2} p={3} borderWidth={1} borderRadius="md" fontSize="sm">
                        {(() => {
                          const model = LOCAL_MODELS.find(m => m.id === selectedLocalModel)
                          return (
                            <>
                              <Text>模型路径: {model?.path}</Text>
                              <Text>大小: {model?.size}</Text>
                              <Text>格式: {model?.format}</Text>
                              <Text>最后修改: {model?.lastModified}</Text>
                            </>
                          )
                        })()}
                      </Box>
                    )}
                  </FormControl>
                </TabPanel>
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <FormControl>
                      <FormLabel fontWeight="bold">上传模型文件</FormLabel>
                      <Input
                        type="file"
                        accept=".bin,.ckpt,.pt,.pth,.safetensors"
                        onChange={handleModelFileChange}
                        p={1}
                      />
                      <Text mt={1} fontSize="sm" color="gray.500">
                        支持的格式: .bin, .ckpt, .pt, .pth, .safetensors (最大2GB)
                      </Text>
                    </FormControl>
                    
                    {localModelInfo && (
                      <Box>
                        <Text fontSize="sm" mb={2}>
                          文件名: {localModelInfo.name}
                          <br />
                          大小: {(localModelInfo.size / (1024 * 1024)).toFixed(2)} MB
                        </Text>
                        <Progress
                          value={uploadProgress}
                          size="sm"
                          colorScheme="blue"
                          hasStripe
                          isAnimated
                        />
                      </Box>
                    )}
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        )}
      </VStack>
    </Box>
  )
} 