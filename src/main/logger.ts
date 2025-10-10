/**
 * 日志工具 - 将所有日志输出到文件
 */
import { app } from 'electron'
import { promises as fs } from 'fs'
import { join } from 'path'

class Logger {
  private logPath: string
  private logBuffer: string[] = []
  private flushTimer: NodeJS.Timeout | null = null

  constructor() {
    // 日志文件保存在用户的日志目录
    const logDir = app.getPath('logs')
    this.logPath = join(logDir, 'app.log')

    // 启动时清空旧日志
    this.initLogFile()
  }

  private async initLogFile(): Promise<void> {
    try {
      const logDir = app.getPath('logs')
      await fs.mkdir(logDir, { recursive: true })

      // 写入日志开始标记
      const header = `\n${'='.repeat(80)}\n应用启动: ${new Date().toISOString()}\n${'='.repeat(80)}\n`
      await fs.appendFile(this.logPath, header, 'utf-8')

      console.log(`[Logger] 日志文件: ${this.logPath}`)
    } catch (error) {
      console.error('[Logger] 初始化日志文件失败:', error)
    }
  }

  /**
   * 记录日志到文件
   */
  private async writeLog(level: string, ...args: unknown[]): Promise<void> {
    const timestamp = new Date().toISOString()
    const message = args.map(arg =>
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ')

    const logLine = `[${timestamp}] [${level}] ${message}\n`

    // 缓冲日志，批量写入
    this.logBuffer.push(logLine)

    // 延迟写入（避免频繁 IO）
    if (this.flushTimer) {
      clearTimeout(this.flushTimer)
    }

    this.flushTimer = setTimeout(() => {
      this.flush()
    }, 500)
  }

  /**
   * 刷新缓冲区到文件
   */
  private async flush(): Promise<void> {
    if (this.logBuffer.length === 0) return

    try {
      const content = this.logBuffer.join('')
      await fs.appendFile(this.logPath, content, 'utf-8')
      this.logBuffer = []
    } catch (error) {
      console.error('[Logger] 写入日志失败:', error)
    }
  }

  /**
   * 获取日志文件路径
   */
  getLogPath(): string {
    return this.logPath
  }

  /**
   * 读取日志内容
   */
  async readLogs(): Promise<string> {
    try {
      return await fs.readFile(this.logPath, 'utf-8')
    } catch (error) {
      return `读取日志失败: ${error}`
    }
  }

  // 封装不同级别的日志方法
  log(...args: unknown[]): void {
    console.log(...args)
    this.writeLog('INFO', ...args)
  }

  error(...args: unknown[]): void {
    console.error(...args)
    this.writeLog('ERROR', ...args)
  }

  warn(...args: unknown[]): void {
    console.warn(...args)
    this.writeLog('WARN', ...args)
  }

  info(...args: unknown[]): void {
    console.info(...args)
    this.writeLog('INFO', ...args)
  }
}

// 导出单例
export const logger = new Logger()
