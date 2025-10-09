import { useState } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState<string>('请选择 Excel 文件开始')
  const [loading, setLoading] = useState<boolean>(false)
  const [progress, setProgress] = useState<number>(0)

  const handleSelectFile = async () => {
    try {
      setLoading(true)
      setStatus('选择文件中...')
      setProgress(10)

      const filePath = await window.api.selectExcelFile()

      if (!filePath) {
        setStatus('未选择文件')
        setLoading(false)
        setProgress(0)
        return
      }

      setStatus(`正在处理: ${filePath.split('/').pop()}`)
      setProgress(20)

      // 步骤 1: 处理 Excel
      const result = await window.api.processExcel(filePath)

      if (!result.success) {
        await window.api.showErrorDialog(result.error || '处理失败')
        setStatus('处理失败')
        setLoading(false)
        setProgress(0)
        return
      }

      setStatus('正在生成 Mermaid 图表...')
      setProgress(40)

      // 步骤 2: 生成 Mermaid 图片（本地）
      const imageResult = await window.api.generateMermaidImages(result.chapters)

      if (!imageResult.success) {
        await window.api.showErrorDialog(imageResult.error || '图表生成失败')
        setStatus('图表生成失败')
        setLoading(false)
        setProgress(0)
        return
      }

      setStatus('正在生成 Word 文档...')
      setProgress(70)

      // 步骤 3: 生成 Word 文档
      const wordResult = await window.api.generateWord(result.chapters, imageResult.imageMapping)

      if (!wordResult.success) {
        await window.api.showErrorDialog(wordResult.error || 'Word 文档生成失败')
        setStatus('文档生成失败')
        setLoading(false)
        setProgress(0)
        return
      }

      setProgress(100)
      setStatus('文档生成成功！')

      // 显示成功提示
      await window.api.showSuccessDialog(wordResult.output_path)

      setLoading(false)
      setProgress(0)
      setStatus('请选择 Excel 文件开始')
    } catch (error: any) {
      console.error('处理错误:', error)
      await window.api.showErrorDialog(error.message || '未知错误')
      setStatus('处理失败')
      setLoading(false)
      setProgress(0)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📝 需求说明书生成工具</h1>
        <p>基于 Excel 自动生成软件需求说明书</p>
      </div>

      <div className="main-content">
        <div className="status-card">
          <div className="status-text">{status}</div>

          {loading && (
            <div className="progress-container">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
              <div className="progress-label">{progress}%</div>
            </div>
          )}
        </div>

        <button className="select-button" onClick={handleSelectFile} disabled={loading}>
          {loading ? '处理中...' : '选择 Excel 文件'}
        </button>

        <div className="info-box">
          <h3>使用说明：</h3>
          <ol>
            <li>点击"选择 Excel 文件"按钮</li>
            <li>选择包含需求数据的 Excel 文件（需包含"功能点拆分表"工作表）</li>
            <li>系统会自动：
              <ul>
                <li>解析 Excel 数据</li>
                <li>调用 AI 生成功能描述</li>
                <li>生成 Mermaid 流程图</li>
                <li>输出 Word 格式的需求说明书</li>
              </ul>
            </li>
            <li>选择保存位置</li>
            <li>完成！</li>
          </ol>
        </div>
      </div>

      <div className="footer">
        <p>Powered by Electron + React + Python + AI</p>
      </div>
    </div>
  )
}

export default App
