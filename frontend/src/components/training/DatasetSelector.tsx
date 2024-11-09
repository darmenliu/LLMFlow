import React, { useState } from 'react'
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
  Text,
  Progress,
  useToast,
  Button,
  HStack,
} from "@chakra-ui/react"
import { ViewIcon } from '@chakra-ui/icons'

interface DatasetOption {
  id: string
  name: string
  description: string
  size: string
  samples: number
  format: string
}

interface LocalDatasetOption {
  id: string
  name: string
  path: string
  size: string
  format: string
  lastModified: string
  samples: number
}

// 模拟在线数据集列表
const ONLINE_DATASETS: DatasetOption[] = [
  {
    id: "alpaca-zh",
    name: "Alpaca 中文指令数据集",
    description: "中文指令精调数据集，包含52K条高质量指令数据",
    size: "15MB",
    samples: 52000,
    format: "json"
  },
  {
    id: "belle-math",
    name: "BELLE 数学数据集",
    description: "数学解题指令数据集，包含10K条数学题目及解答",
    size: "8MB",
    samples: 10000,
    format: "jsonl"
  },
  {
    id: "medical-qa",
    name: "医疗问答数据集",
    description: "中文医疗问答数据，包含20K条医疗咨询对话",
    size: "12MB",
    samples: 20000,
    format: "json"
  }
]

// 模拟本地数据集列表
const LOCAL_DATASETS: LocalDatasetOption[] = [
  {
    id: "custom-qa",
    name: "自定义问答数据",
    path: "/datasets/custom-qa.json",
    size: "5MB",
    format: "json",
    lastModified: "2024-03-20",
    samples: 8000
  },
  {
    id: "fine-tune-data",
    name: "历史微调数据",
    path: "/datasets/fine-tune-data.jsonl",
    size: "18MB",
    format: "jsonl",
    lastModified: "2024-03-18",
    samples: 25000
  }
]

interface DatasetSelectorProps {
  onDatasetSelect?: (datasetInfo: {
    type: "online" | "local" | "upload"
    datasetId?: string
    file?: File
    localPath?: string
  }) => void
}

export default function DatasetSelector({ onDatasetSelect }: DatasetSelectorProps) {
  const [sourceType, setSourceType] = useState<"online" | "local" | "upload">("online")
  const [selectedDataset, setSelectedDataset] = useState<string>("")
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const toast = useToast()

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 1024 * 1024 * 500) { // 500MB限制
        toast({
          title: "文件过大",
          description: "数据文件不能超过500MB",
          status: "error",
          duration: 3000,
        })
        return
      }

      setUploadFile(file)
      let progress = 0
      const interval = setInterval(() => {
        progress += 5
        setUploadProgress(progress)
        if (progress >= 100) {
          clearInterval(interval)
          toast({
            title: "数据文件已就绪",
            description: `${file.name} 已准备完成`,
            status: "success",
            duration: 3000,
          })
          onDatasetSelect?.({
            type: "upload",
            file: file
          })
        }
      }, 100)
    }
  }

  const handleDatasetChange = (value: string) => {
    setSelectedDataset(value)
    if (sourceType === "online") {
      onDatasetSelect?.({
        type: "online",
        datasetId: value
      })
    } else if (sourceType === "local") {
      const dataset = LOCAL_DATASETS.find(d => d.id === value)
      onDatasetSelect?.({
        type: "local",
        datasetId: value,
        localPath: dataset?.path
      })
    }
  }

  const handlePreview = () => {
    toast({
      title: "数据预览功能开发中",
      description: "该功能将在后续版本中提供",
      status: "info",
      duration: 3000,
    })
  }

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white" shadow="sm">
      <VStack spacing={6} align="stretch">
        <FormControl>
          <FormLabel fontWeight="bold">数据来源</FormLabel>
          <RadioGroup
            value={sourceType}
            onChange={(value: "online" | "local" | "upload") => {
              setSourceType(value)
              setSelectedDataset("")
              setUploadFile(null)
              setUploadProgress(0)
            }}
          >
            <Stack direction="row" spacing={5}>
              <Radio value="online">使用在线数据集</Radio>
              <Radio value="local">使用本地数据集</Radio>
              <Radio value="upload">上传新数据集</Radio>
            </Stack>
          </RadioGroup>
        </FormControl>

        {sourceType === "upload" ? (
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel fontWeight="bold">上传数据文件</FormLabel>
              <Input
                type="file"
                accept=".json,.jsonl,.csv,.txt"
                onChange={handleFileUpload}
                p={1}
              />
              <Text mt={1} fontSize="sm" color="gray.500">
                支持的格式: .json, .jsonl, .csv, .txt (最大500MB)
              </Text>
            </FormControl>
            
            {uploadFile && (
              <Box>
                <Text fontSize="sm" mb={2}>
                  文件名: {uploadFile.name}
                  <br />
                  大小: {(uploadFile.size / (1024 * 1024)).toFixed(2)} MB
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
        ) : (
          <FormControl>
            <HStack justify="space-between" align="center" mb={2}>
              <FormLabel fontWeight="bold" mb={0}>
                {sourceType === "online" ? "选择在线数据集" : "选择本地数据集"}
              </FormLabel>
              <Button
                size="sm"
                leftIcon={<ViewIcon />}
                variant="outline"
                onClick={handlePreview}
                isDisabled={!selectedDataset}
              >
                预览数据
              </Button>
            </HStack>
            <Select
              placeholder={`请选择${sourceType === "online" ? "在线" : "本地"}数据集`}
              value={selectedDataset}
              onChange={(e) => handleDatasetChange(e.target.value)}
            >
              {(sourceType === "online" ? ONLINE_DATASETS : LOCAL_DATASETS).map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.samples.toLocaleString()} 条数据)
                </option>
              ))}
            </Select>
            
            {selectedDataset && (
              <Box mt={2} p={3} borderWidth={1} borderRadius="md" fontSize="sm">
                {(() => {
                  const dataset = (sourceType === "online" ? ONLINE_DATASETS : LOCAL_DATASETS)
                    .find(d => d.id === selectedDataset)
                  if (!dataset) return null

                  if (sourceType === "online") {
                    const onlineDataset = dataset as DatasetOption
                    return (
                      <VStack align="stretch" spacing={1}>
                        <Text>{onlineDataset.description}</Text>
                        <HStack spacing={4}>
                          <Text>大小: {onlineDataset.size}</Text>
                          <Text>格式: {onlineDataset.format}</Text>
                        </HStack>
                      </VStack>
                    )
                  } else {
                    const localDataset = dataset as LocalDatasetOption
                    return (
                      <VStack align="stretch" spacing={1}>
                        <Text>路径: {localDataset.path}</Text>
                        <HStack spacing={4}>
                          <Text>大小: {localDataset.size}</Text>
                          <Text>格式: {localDataset.format}</Text>
                          <Text>最后修改: {localDataset.lastModified}</Text>
                        </HStack>
                      </VStack>
                    )
                  }
                })()}
              </Box>
            )}
          </FormControl>
        )}
      </VStack>
    </Box>
  )
} 