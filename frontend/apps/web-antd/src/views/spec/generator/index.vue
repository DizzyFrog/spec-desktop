<template>
  <div class="p-4">
    <!-- 缓存统计卡片 -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div>
            <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">缓存统计</h3>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ cacheStats ? formatSize(cacheStats.total_size) : '--' }}
            </p>
          </div>
          <div class="text-sm text-gray-600 dark:text-gray-400" v-if="cacheStats">
            <div>图片缓存: {{ cacheStats.cache_files }} 个 ({{ formatSize(cacheStats.cache_size) }})</div>
            <div>上传文件: {{ cacheStats.upload_files }} 个 ({{ formatSize(cacheStats.upload_size) }})</div>
            <div>输出文档: {{ cacheStats.output_files }} 个 ({{ formatSize(cacheStats.output_size) }})</div>
          </div>
        </div>
        <div class="flex space-x-2">
          <button
            @click="loadCacheStats"
            :disabled="loadingStats"
            class="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
          >
            {{ loadingStats ? '刷新中...' : '刷新' }}
          </button>
          <button
            @click="showClearConfirm"
            :disabled="!cacheStats || cacheStats.total_size === 0 || clearingCache"
            class="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ clearingCache ? '清理中...' : '清理缓存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主功能区 -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <h1 class="text-2xl font-bold mb-4">需求说明书生成器</h1>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">
            选择 Excel 文件
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleFileChange"
            class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
          />
        </div>

        <div v-if="selectedFile" class="text-sm text-gray-600 dark:text-gray-400">
          已选择: {{ selectedFile.name }}
        </div>

        <button
          @click="handleUpload"
          :disabled="!selectedFile || loading"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ loading ? '处理中...' : '开始生成' }}
        </button>

        <div v-if="progress" class="mt-4">
          <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {{ progress }}
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
            <div
              class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              :style="{ width: progressPercent + '%' }"
            ></div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg">
          <div class="font-semibold mb-2">❌ {{ error }}</div>

          <!-- 验证错误详情 -->
          <div v-if="validationErrors.length > 0" class="mt-3 space-y-2">
            <div v-for="(err, index) in validationErrors" :key="index" class="pl-4 border-l-2 border-red-400">
              <div class="font-medium">{{ err.message }}</div>
              <div class="text-sm opacity-80 mt-1">📍 位置: {{ err.location }}</div>
              <div class="text-sm opacity-90 mt-1 whitespace-pre-line">{{ err.details }}</div>
            </div>
          </div>
        </div>

        <!-- 警告信息 -->
        <div v-if="validationWarnings.length > 0" class="p-4 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 rounded-lg">
          <div class="font-semibold mb-2">⚠️ 验证警告 (可继续生成，但建议修改)</div>
          <div class="mt-3 space-y-2">
            <div v-for="(warn, index) in validationWarnings" :key="index" class="pl-4 border-l-2 border-yellow-400">
              <div class="font-medium">{{ warn.message }}</div>
              <div class="text-sm opacity-80 mt-1">📍 位置: {{ warn.location }}</div>
              <div class="text-sm opacity-90 mt-1 whitespace-pre-line">{{ warn.details }}</div>
            </div>
          </div>
        </div>

        <!-- 成功信息 -->
        <div v-if="success" class="p-4 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg">
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAccessStore } from '@vben/stores';

const accessStore = useAccessStore();

const selectedFile = ref<File | null>(null);
const loading = ref(false);
const progress = ref('');
const progressPercent = ref(0);
const error = ref('');
const success = ref('');

// 缓存管理相关
interface CacheStats {
  user_id: number;
  username: string;
  cache_size: number;
  upload_size: number;
  output_size: number;
  total_size: number;
  cache_files: number;
  upload_files: number;
  output_files: number;
  total_files: number;
  total_size_mb: number;
}

const cacheStats = ref<CacheStats | null>(null);
const loadingStats = ref(false);
const clearingCache = ref(false);

// 验证错误和警告
interface ValidationIssue {
  type: string;
  message: string;
  location: string;
  details: string;
}

const validationErrors = ref<ValidationIssue[]>([]);
const validationWarnings = ref<ValidationIssue[]>([]);

// 获取认证 header
const getAuthHeaders = () => {
  const token = accessStore.accessToken;
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// 加载缓存统计
const loadCacheStats = async () => {
  loadingStats.value = true;
  try {
    const response = await fetch('/api/cache/stats', {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('获取缓存统计失败');
    }

    const result = await response.json();
    cacheStats.value = result.data;
  } catch (err) {
    console.error('获取缓存统计失败:', err);
  } finally {
    loadingStats.value = false;
  }
};

// 显示清理确认对话框
const showClearConfirm = () => {
  if (!cacheStats.value) return;

  const confirmed = confirm(
    `确定要清理缓存吗？\n\n` +
    `图片缓存: ${cacheStats.value.cache_files} 个文件 (${formatSize(cacheStats.value.cache_size)})\n` +
    `上传文件: ${cacheStats.value.upload_files} 个文件 (${formatSize(cacheStats.value.upload_size)})\n` +
    `输出文档: ${cacheStats.value.output_files} 个文件 (${formatSize(cacheStats.value.output_size)})\n\n` +
    `总计: ${formatSize(cacheStats.value.total_size)}\n\n` +
    `此操作不可撤销！`
  );

  if (confirmed) {
    clearCache();
  }
};

// 清理缓存
const clearCache = async () => {
  clearingCache.value = true;
  try {
    const response = await fetch('/api/cache/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        clear_cache: true,
        clear_uploads: true,
        clear_outputs: true,
      }),
    });

    if (!response.ok) {
      throw new Error('清理缓存失败');
    }

    const result = await response.json();
    success.value = `缓存清理成功！${result.data.message}`;

    // 重新加载统计
    await loadCacheStats();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '清理缓存失败';
  } finally {
    clearingCache.value = false;
  }
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
    error.value = '';
    success.value = '';
  }
};

const handleUpload = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  error.value = '';
  success.value = '';
  validationErrors.value = [];
  validationWarnings.value = [];
  progress.value = '准备上传文件...';
  progressPercent.value = 5;

  try {
    // 步骤 1: 上传文件
    const formData = new FormData();
    formData.append('file', selectedFile.value);

    progress.value = '上传文件中...';
    progressPercent.value = 10;

    const uploadResponse = await fetch('/api/upload/excel', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });

    if (!uploadResponse.ok) {
      throw new Error('文件上传失败');
    }

    const uploadResult = await uploadResponse.json();
    const filePath = uploadResult.data.file_path;

    // 步骤 2: 处理 Excel 文件
    progress.value = '解析 Excel 文件...';
    progressPercent.value = 30;

    const processResponse = await fetch('/api/generate/process-excel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ file_path: filePath }),
    });

    if (!processResponse.ok) {
      throw new Error('Excel 解析失败');
    }

    const processResult = await processResponse.json();

    // 检查验证结果
    if (processResult.data.validation) {
      // 有验证错误
      validationErrors.value = processResult.data.validation.errors || [];
      validationWarnings.value = processResult.data.validation.warnings || [];

      if (!processResult.data.success) {
        throw new Error('Excel 文件验证失败，请查看详细错误信息');
      }
    }

    // 处理警告（如果有）
    if (processResult.data.warnings) {
      validationWarnings.value = processResult.data.warnings;
    }

    const chapters = processResult.data.chapters;

    // 步骤 3: 生成 Mermaid 图片
    progress.value = '生成图表中...';
    progressPercent.value = 50;

    const mermaidResponse = await fetch('/api/generate/mermaid-images', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ chapters }),
    });

    if (!mermaidResponse.ok) {
      throw new Error('图表生成失败');
    }

    const mermaidResult = await mermaidResponse.json();
    const imageMapping = mermaidResult.data.imageMapping;

    // 步骤 4: 生成 Word 文档
    progress.value = '生成 Word 文档...';
    progressPercent.value = 70;

    const wordResponse = await fetch('/api/generate/generate-word', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        chapters,
        image_mapping: imageMapping,
        output_filename: '需求说明书.docx'
      }),
    });

    if (!wordResponse.ok) {
      throw new Error('Word 文档生成失败');
    }

    // 步骤 5: 下载文件
    progress.value = '下载文档...';
    progressPercent.value = 90;

    // 直接从响应中获取文件 blob
    const blob = await wordResponse.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '需求说明书.docx';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    progress.value = '完成！';
    progressPercent.value = 100;
    success.value = '需求说明书生成成功！';

  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
    progressPercent.value = 0;
  } finally {
    loading.value = false;
    setTimeout(() => {
      progress.value = '';
      progressPercent.value = 0;
    }, 3000);
  }
};

// 页面加载时获取缓存统计
onMounted(() => {
  loadCacheStats();
});
</script>
