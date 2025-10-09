import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: {
      selectExcelFile: () => Promise<string | null>
      processExcel: (filePath: string) => Promise<any>
      generateMermaidImages: (chapters: any[]) => Promise<any>
      generateWord: (chapters: any[], imageMapping: Record<string, string>) => Promise<any>
      showSuccessDialog: (filePath: string) => Promise<void>
      showErrorDialog: (errorMessage: string) => Promise<void>
    }
  }
}
