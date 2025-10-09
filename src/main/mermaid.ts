/**
 * Mermaid 图表生成工具
 * 使用 @mermaid-js/mermaid-cli 在本地生成 PNG 图片
 */
import { spawn } from 'child_process'
import { promises as fs } from 'fs'
import { join } from 'path'
import { tmpdir } from 'os'
import crypto from 'crypto'

export class MermaidGenerator {
  private cacheDir: string

  constructor(cacheDir?: string) {
    this.cacheDir = cacheDir || join(tmpdir(), 'spec-desktop-cache')
  }

  /**
   * 确保缓存目录存在
   */
  private async ensureCacheDir(): Promise<void> {
    try {
      await fs.mkdir(this.cacheDir, { recursive: true })
    } catch (error) {
      console.error('创建缓存目录失败:', error)
    }
  }

  /**
   * 生成内容的 hash 值
   */
  private hash(content: string): string {
    return crypto.createHash('md5').update(content).digest('hex')
  }

  /**
   * 生成 Mermaid PNG 图片
   * @param mermaidCode Mermaid 语法代码
   * @param outputPath 输出文件路径（可选，不提供则使用缓存）
   * @returns 生成的图片文件路径
   */
  async generatePNG(mermaidCode: string, outputPath?: string): Promise<string> {
    await this.ensureCacheDir()

    // 如果没有提供输出路径，使用基于 hash 的缓存路径
    const finalPath = outputPath || join(this.cacheDir, `${this.hash(mermaidCode)}.png`)

    // 检查缓存
    try {
      await fs.access(finalPath)
      console.log('使用缓存的 Mermaid 图片:', finalPath)
      return finalPath
    } catch {
      // 缓存不存在，继续生成
    }

    // 创建临时的 .mmd 文件
    const tempMmdPath = join(this.cacheDir, `temp_${Date.now()}.mmd`)
    await fs.writeFile(tempMmdPath, mermaidCode, 'utf-8')

    return new Promise((resolve, reject) => {
      // 使用 npx mmdc 命令生成图片
      const mmdc = spawn('npx', ['mmdc', '-i', tempMmdPath, '-o', finalPath], {
        shell: true
      })

      let stderr = ''

      mmdc.stderr?.on('data', (data) => {
        stderr += data.toString()
      })

      mmdc.on('close', async (code) => {
        // 删除临时文件
        try {
          await fs.unlink(tempMmdPath)
        } catch (error) {
          console.error('删除临时文件失败:', error)
        }

        if (code === 0) {
          console.log('Mermaid 图片生成成功:', finalPath)
          resolve(finalPath)
        } else {
          reject(new Error(`Mermaid 生成失败: ${stderr}`))
        }
      })

      mmdc.on('error', (error) => {
        reject(error)
      })
    })
  }

  /**
   * 生成结构图（flowchart）
   * @param featureName 功能名称
   * @param processes 功能过程列表
   * @returns 图片文件路径
   */
  async generateStructureChart(featureName: string, processes: string[]): Promise<string> {
    const nodeId = (text: string) => 'N' + this.hash(text).substring(0, 8)
    const escape = (text: string) => text.replace(/"/g, '\\"')

    const keyId = nodeId(featureName)
    const escapedKey = escape(featureName)

    let content = `    ${keyId}["${escapedKey}"]\n`

    for (const process of processes) {
      const processId = nodeId(process)
      const escapedProcess = escape(process)
      content += `    ${processId}["${escapedProcess}"]\n`
      content += `    ${keyId} --> ${processId}\n`
    }

    const mermaidCode = `flowchart TD\n${content}`
    return await this.generatePNG(mermaidCode)
  }

  /**
   * 生成流程图（sequenceDiagram）
   * @param roles 角色列表 [角色A, 角色B, 角色C]
   * @param processes 过程列表
   * @returns 图片文件路径
   */
  async generateFlowChart(roles: string[], processes: string[]): Promise<string> {
    const escape = (text: string) => text.replace(/"/g, '\\"').replace(/\n/g, ' ').replace(/\r/g, ' ')

    const [A, B, C] = roles
    const step1 = processes[0]
    const step2 = processes[Math.floor(processes.length / 2)]
    const step3 = processes[processes.length - 1]

    const mermaidCode = `sequenceDiagram
    participant a as "${escape(A)}"
    participant b as "${escape(B)}"
    participant c as "${escape(C)}"

    a ->> b: "${escape(step1)}"
    b ->> c: "${escape(step2)}"
    b ->> a: "${escape(step3)}"`

    return await this.generatePNG(mermaidCode)
  }
}

// 导出单例
export const mermaidGenerator = new MermaidGenerator()
