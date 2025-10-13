<template>
  <div class="p-4">
    <n-card title="需求规格说明书生成器">
      <n-spin :show="loading">
        <div class="flex flex-col gap-6">
          <n-steps :current="currentStep" :status="stepStatus">
            <n-step title="上传文档" description="上传包含需求的 Excel 文件。" />
            <n-step title="处理数据" description="分析文件内容并生成图表。" />
            <n-step title="生成文档" description="将所有内容合并为 Word 文档。" />
            <n-step title="完成" description="下载生成的说明书。" />
          </n-steps>

          <div v-if="currentStep === 1">
            <n-upload
              directory-dnd
              :max="1"
              :default-upload="false"
              @change="handleFileChange"
            >
              <n-upload-dragger>
                <div style="margin-bottom: 12px">
                  <n-icon size="48" :depth="3">
                    <lucide:archive />
                  </n-icon>
                </div>
                <n-text style="font-size: 16px">点击或拖拽文件到这里</n-text>
                <n-p depth="3" style="margin: 8px 0 0 0">
                  请上传格式正确的 Excel 文件
                </n-p>
              </n-upload-dragger>
            </n-upload>
          </div>

          <div v-if="alertMessage" class="mt-4">
            <n-alert :title="stepStatus === 'error' ? '出错了' : '提示'" :type="stepStatus === 'error' ? 'error' : 'info'" closable>
              {{ alertMessage }}
            </n-alert>
          </div>

          <div class="flex justify-center">
            <n-button
              type="primary"
              size="large"
              @click="handleStartProcessing"
              :disabled="!selectedFile || loading"
            >
              开始生成
            </n-button>
          </div>
        </div>
        <template #description>
          {{ loadingText }}
        </template>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMessage } from 'naive-ui';
import type { UploadFileInfo } from 'naive-ui';
import { uploadExcel, processExcel, generateMermaidImages, generateWord } from '#/api/spec';

const message = useMessage();

const loading = ref(false);
const loadingText = ref('');
const currentStep = ref(1);
const stepStatus = ref<'process' | 'finish' | 'error' | 'wait'>('process');
const alertMessage = ref('');

const selectedFile = ref<File | null>(null);

// Store processed data
const processedData = ref<any>(null);
const imageMap = ref<Record<string, string> | null>(null);

function handleFileChange(options: { file: UploadFileInfo }) {
  if (options.file.file) {
    selectedFile.value = options.file.file;
    alertMessage.value = `已选择文件: ${options.file.name}`;
    stepStatus.value = 'process';
  } else {
    selectedFile.value = null;
  }
}

async function handleStartProcessing() {
  if (!selectedFile.value) {
    message.error('请先选择一个 Excel 文件');
    return;
  }

  loading.value = true;
  stepStatus.value = 'process';
  alertMessage.value = '';

  try {
    // Step 1: Upload Excel
    currentStep.value = 1;
    loadingText.value = '正在上传 Excel 文件...';
    const uploadResult = await uploadExcel(selectedFile.value);
    const filePath = uploadResult.data.file_path;
    message.success('文件上传成功');

    // Step 2: Process Excel & Generate Mermaid Images
    currentStep.value = 2;
    loadingText.value = '正在处理数据，生成章节和图表...';
    const processResult = await processExcel(filePath);
    processedData.value = processResult.data;

    const mermaidResult = await generateMermaidImages(processedData.value.chapters);
    imageMap.value = mermaidResult.data.imageMapping;
    message.success('数据处理和图表生成成功');

    // Step 3: Generate Word Document
    currentStep.value = 3;
    loadingText.value = '正在生成 Word 文档...';
    await generateWord(processedData.value.chapters, imageMap.value || {});
    message.success('Word 文档生成成功，即将开始下载');

    // Step 4: Complete
    currentStep.value = 4;
    stepStatus.value = 'finish';
    loadingText.value = '处理完成！';
    alertMessage.value = '所有步骤已成功完成，请检查您的下载。';

  } catch (error: any) {
    console.error('处理失败:', error);
    stepStatus.value = 'error';
    const errorMsg = error.response?.data?.detail || error.message || '发生未知错误';
    alertMessage.value = `在步骤 ${currentStep.value} 出错: ${errorMsg}`;
    message.error(`处理失败: ${errorMsg}`);
  } finally {
    loading.value = false;
    loadingText.value = '';
  }
}
</script>

<style scoped>
/* Add any custom styles here */
</style>
