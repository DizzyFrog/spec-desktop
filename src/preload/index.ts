import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  // 选择 Excel 文件
  selectExcelFile: () => ipcRenderer.invoke('select-excel-file'),

  // 处理 Excel
  processExcel: (filePath: string) => ipcRenderer.invoke('process-excel', filePath),

  // 生成 Mermaid 图片
  generateMermaidImages: (chapters: any[]) =>
    ipcRenderer.invoke('generate-mermaid-images', chapters),

  // 生成 Word 文档
  generateWord: (chapters: any[], imageMapping: Record<string, string>) =>
    ipcRenderer.invoke('generate-word', chapters, imageMapping),

  // 显示成功对话框
  showSuccessDialog: (filePath: string) => ipcRenderer.invoke('show-success-dialog', filePath),

  // 显示错误对话框
  showErrorDialog: (errorMessage: string) => ipcRenderer.invoke('show-error-dialog', errorMessage)
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}
