/**
 * IPC 处理器 - 主进程
 * 处理前端请求，调用后端 API 和本地 Mermaid 生成
 */
import { ipcMain, dialog } from 'electron'
import { promises as fs } from 'fs'
import axios from 'axios'
import { mermaidGenerator } from './mermaid'

const BACKEND_URL = 'http://127.0.0.1:8000'

/**
 * 注册所有 IPC 处理器
 */
export function registerIpcHandlers(): void {
  // 1. 选择 Excel 文件
  ipcMain.handle('select-excel-file', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }]
    })

    if (result.canceled || result.filePaths.length === 0) {
      return null
    }

    return result.filePaths[0]
  })

  // 2. 上传并处理 Excel
  ipcMain.handle('process-excel', async (_, filePath: string) => {
    try {
      // 直接调用后端处理（后端会读取文件）
      const processResponse = await axios.post(`${BACKEND_URL}/api/generate/process-excel`, {
        file_path: filePath
      })

      return processResponse.data
    } catch (error: any) {
      console.error('处理 Excel 失败:', error)
      return {
        success: false,
        error: error.response?.data?.detail || error.message || '处理失败'
      }
    }
  })

  // 3. 生成 Mermaid 图片（本地，并行优化）
  ipcMain.handle('generate-mermaid-images', async (_, chapters: any[]) => {
    try {
      const imageMapping: Record<string, string> = {}

      // 收集所有图片生成任务
      const tasks: Array<{
        key: string
        promise: Promise<string>
      }> = []

      for (const chapter of chapters) {
        // 生成结构图
        const structureKey = `structure_${chapter.name}`
        tasks.push({
          key: structureKey,
          promise: mermaidGenerator.generateStructureChart(
            chapter.name,
            chapter.functions
          )
        })

        // 生成流程图
        if (chapter.features) {
          for (const feature of chapter.features) {
            const flowKey = `flow_${feature.scenario}`
            tasks.push({
              key: flowKey,
              promise: mermaidGenerator.generateFlowChart(
                feature.role,
                feature.process
              )
            })
          }
        }
      }

      console.log(`开始并行生成 ${tasks.length} 张 Mermaid 图片...`)
      const startTime = Date.now()

      // 限制并发数，避免同时启动过多进程（每个 mmdc 会启动 Puppeteer）
      const CONCURRENCY_LIMIT = 5
      const results: PromiseSettledResult<string>[] = []

      for (let i = 0; i < tasks.length; i += CONCURRENCY_LIMIT) {
        const batch = tasks.slice(i, i + CONCURRENCY_LIMIT)
        const batchResults = await Promise.allSettled(batch.map(t => t.promise))
        results.push(...batchResults)
        console.log(`完成批次 ${Math.floor(i / CONCURRENCY_LIMIT) + 1}/${Math.ceil(tasks.length / CONCURRENCY_LIMIT)}`)
      }

      // 处理结果
      results.forEach((result, index) => {
        const task = tasks[index]
        if (result.status === 'fulfilled') {
          imageMapping[task.key] = result.value
          console.log(`✓ ${task.key}`)
        } else {
          console.error(`✗ ${task.key} 失败:`, result.reason)
        }
      })

      const duration = ((Date.now() - startTime) / 1000).toFixed(2)
      console.log(`所有图片生成完成，耗时 ${duration} 秒`)

      return {
        success: true,
        imageMapping
      }
    } catch (error: any) {
      console.error('生成 Mermaid 图片失败:', error)
      return {
        success: false,
        error: error.message
      }
    }
  })

  // 4. 生成 Word 文档
  ipcMain.handle(
    'generate-word',
    async (_, chapters: any[], imageMapping: Record<string, string>) => {
      try {
        const response = await axios.post(`${BACKEND_URL}/api/generate/generate-word`, {
          chapters,
          image_mapping: imageMapping,
          output_filename: '需求说明书.docx'
        })

        if (response.data.success) {
          // 让用户选择保存位置
          const saveResult = await dialog.showSaveDialog({
            title: '保存需求说明书',
            defaultPath: '需求说明书.docx',
            filters: [{ name: 'Word Documents', extensions: ['docx'] }]
          })

          if (!saveResult.canceled && saveResult.filePath) {
            // 复制文件到用户选择的位置
            await fs.copyFile(response.data.output_path, saveResult.filePath)

            return {
              success: true,
              output_path: saveResult.filePath
            }
          }
        }

        return response.data
      } catch (error: any) {
        console.error('生成 Word 文档失败:', error)
        return {
          success: false,
          error: error.message
        }
      }
    }
  )

  // 5. 显示成功对话框
  ipcMain.handle('show-success-dialog', async (_, filePath: string) => {
    await dialog.showMessageBox({
      type: 'info',
      title: '生成成功',
      message: '需求说明书已生成！',
      detail: `文件保存在：\n${filePath}`,
      buttons: ['确定']
    })
  })

  // 6. 显示错误对话框
  ipcMain.handle('show-error-dialog', async (_, errorMessage: string) => {
    await dialog.showMessageBox({
      type: 'error',
      title: '错误',
      message: '处理失败',
      detail: errorMessage,
      buttons: ['确定']
    })
  })
}
