# 快速启动指南

## 🚀 一键启动

```bash
# 1. 安装前端依赖（首次运行）
npm install

# 2. 安装后端依赖（首次运行）
cd backend
uv sync
cd ..

# 3. 启动应用
npm run dev
```

## ✅ 前置要求

- **Node.js** >= 18
- **Python** >= 3.9
- **uv** - Python 包管理器
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 📝 AI 配置

编辑 `backend/.env`:
```env
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_API_KEY=你的API密钥
AI_MODEL=qwen-long
```

## 🎯 使用步骤

1. 启动应用后，点击**"选择 Excel 文件"**
2. 选择包含**"功能点拆分表"**工作表的 Excel 文件
3. 等待自动处理（10-60秒，取决于数据量）
4. 选择保存位置
5. 完成！Word 文档已生成

## 📊 Excel 格式要求

工作表名称：**功能点拆分表**

必需列：
- `功能用户需求`
- `触发事件`
- `功能过程`
- `子过程描述`
- `数据组`
- `功能用户`
- `角色` （需要 3 个角色，用中文逗号分隔）

## 🔧 常见问题

### Mermaid 图表生成失败
确保已安装 `@mermaid-js/mermaid-cli`:
```bash
npm install
```

### 后端启动失败
检查 Python 依赖:
```bash
cd backend
uv sync
```

### AI 调用失败
检查 `backend/.env` 中的 API Key 是否正确。

## 📦 打包发布

```bash
# macOS
npm run build:mac

# Windows
npm run build:win

# Linux
npm run build:linux
```

打包后的应用包含：
- Electron 前端
- Python 后端（可执行文件）
- Mermaid CLI
- 所有依赖

用户无需安装 Python 或任何依赖即可运行！

## 🎨 技术栈

- **前端**: Electron + React + TypeScript
- **后端**: FastAPI + Python (uv)
- **AI**: 阿里云通义千问
- **图表**: Mermaid CLI（本地生成）
- **文档**: python-docx

## 📂 项目结构

```
spec-desktop/
├── src/
│   ├── main/          # Electron 主进程
│   │   ├── index.ts
│   │   ├── ipc-handlers.ts  # IPC 通信
│   │   └── mermaid.ts       # Mermaid 生成
│   ├── preload/       # 预加载脚本
│   └── renderer/      # React UI
├── backend/
│   ├── app/
│   │   ├── services/  # 核心服务
│   │   └── routers/   # API 路由
│   ├── pyproject.toml
│   └── .env          # AI 配置
└── package.json
```

## 💡 提示

- Excel 文件越大，处理时间越长
- AI 生成的描述质量取决于输入数据的完整性
- 生成的图片会被缓存，相同内容不会重复生成
- 所有文件处理都在本地完成，无需联网（除了 AI 调用）

## 🆘 获取帮助

查看详细文档: [CLAUDE.md](CLAUDE.md)
