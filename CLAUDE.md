# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Electron desktop application** for automatically generating requirements specification documents. It uses:
- **Frontend**: Electron + React + TypeScript (with Vite)
- **Backend**: FastAPI (Python) with **uv** package manager for Excel parsing and AI-powered document generation
- **Workflow**: Upload Excel → Parse requirements → AI generates content → Mermaid diagrams → Output Word document

The frontend handles Excel uploads and Mermaid diagram rendering (using mermaid-cli), while the backend parses Excel files, calls AI services, and generates Word documents using python-docx.

**Python 包管理**: 后端使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，提供更快的安装速度和更好的依赖解析。

## Development Commands

### Setup
```bash
# 安装前端依赖
npm install

# 安装后端依赖（使用 uv）
cd backend
uv sync  # 自动创建虚拟环境并安装所有依赖
cd ..
```

**前置要求**:
- Node.js >= 18
- Python >= 3.9
- [uv](https://github.com/astral-sh/uv) - 安装命令: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Development
```bash
# 启动 Electron 应用（会自动启动后端服务）
npm run dev

# 仅启动后端服务（用于调试）
npm run dev:backend
```

### Build
```bash
# 构建所有平台（会先打包后端）
npm run build:mac    # Build for macOS (包含 Python 后端)
npm run build:win    # Build for Windows (包含 Python 后端)
npm run build:linux  # Build for Linux (包含 Python 后端)

# 仅构建前端
npm run build        # Type check and build all processes

# 仅打包后端
npm run build:backend  # 使用 PyInstaller 打包后端为可执行文件
```

### Type Checking
```bash
npm run typecheck           # Check both Node and web types
npm run typecheck:node      # Check main/preload process types
npm run typecheck:web       # Check renderer process types
```

### Code Quality
```bash
npm run lint         # Run ESLint with cache
npm run format       # Format code with Prettier
```

## Architecture

### Electron Process Model

This app follows Electron's multi-process architecture:

1. **Main Process** ([src/main/index.ts](src/main/index.ts))
   - Manages application lifecycle and native OS integration
   - Creates BrowserWindow instances
   - **启动和管理 Python 后端服务**（作为子进程）
   - Handles IPC communication with renderer process
   - 应用退出时自动停止后端服务

2. **Preload Script** ([src/preload/index.ts](src/preload/index.ts))
   - Bridges main and renderer processes securely via contextBridge
   - Exposes safe APIs to renderer (currently: `window.electron` and `window.api`)
   - Future: Add custom APIs for Excel upload, backend communication, etc.

3. **Renderer Process** ([src/renderer/src/App.tsx](src/renderer/src/App.tsx))
   - React-based UI running in Chromium
   - Uses IPC to communicate with main process
   - Future: Components for file upload, progress tracking, Mermaid rendering

4. **Backend Process** ([backend/app/main.py](backend/app/main.py))
   - FastAPI 服务器，运行在 `http://127.0.0.1:8000`
   - 由 Electron 主进程自动启动和停止
   - 开发环境：运行 Python 源码
   - 生产环境：运行 PyInstaller 打包的可执行文件

### Build Configuration

- **electron.vite.config.ts**: Configures separate Vite builds for main, preload, and renderer processes
- **TypeScript configs**:
  - `tsconfig.node.json` for main/preload (Node.js environment)
  - `tsconfig.web.json` for renderer (browser environment)
- **Alias**: `@renderer` → `src/renderer/src` for cleaner imports in renderer code

### IPC Communication Pattern

The project uses Electron's IPC (Inter-Process Communication):
- Renderer sends messages via `window.electron.ipcRenderer.send('channel', data)`
- Main process listens via `ipcMain.on('channel', handler)`
- For request-response, use `ipcRenderer.invoke` / `ipcMain.handle` pattern

### Backend Integration

Python 后端已集成到 Electron 应用中：

**后端架构** ([backend/](backend/)):
```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── routers/             # API 路由
│   │   ├── upload.py        # Excel 文件上传
│   │   └── generate.py      # 文档生成
│   ├── services/            # 业务逻辑
│   │   ├── excel_parser.py  # Excel 解析
│   │   ├── ai_service.py    # AI 服务调用
│   │   └── docx_writer.py   # Word 文档生成
│   └── models/
│       └── schemas.py       # Pydantic 数据模型
├── requirements.txt         # Python 依赖
└── build.py                 # PyInstaller 打包脚本
```

**API 端点**:
- `GET /` - 健康检查
- `POST /api/upload/excel` - 上传 Excel 文件
- `POST /api/generate/document` - 生成需求文档
- `POST /api/generate/mermaid` - 生成 Mermaid 图表

**通信流程**:
1. Renderer → Main process (via IPC)
2. Main process → Python Backend (HTTP: `http://127.0.0.1:8000`)
3. Backend 处理并返回结果
4. Main process → Renderer (via IPC)

**Mermaid 图表流程**:
1. Backend 生成 Mermaid 语法字符串
2. Frontend 使用 `@mermaid-js/mermaid-cli` 渲染为图片
3. 图片发送回 Backend
4. Backend 使用 `python-docx` 将图片插入 Word 文档

## Key Implementation Notes

### Backend Process Management
- **开发环境**: 主进程使用 `spawn` 启动 `uv run main.py`
- **生产环境**: 运行打包后的可执行文件 `spec-backend`
- **生命周期管理**: 应用启动时自动启动后端，退出时自动停止（见 `before-quit` 事件）
- **端口**: 固定使用 `8000` 端口
- **包管理**: 使用 uv 管理 Python 依赖，无需手动激活虚拟环境

### Packaging Strategy
1. **前端**: 使用 `electron-builder` 打包 Electron 应用
2. **后端**: 使用 `PyInstaller` 将 Python 后端打包为独立可执行文件
3. **资源打包**: `electron-builder.yml` 配置 `extraResources` 将后端可执行文件包含到应用包中
4. **构建顺序**: `npm run build:mac/win/linux` 会先运行 `build:backend` 再打包前端

### Sandbox Mode
The preload script sets `sandbox: false` in [src/main/index.ts:86](src/main/index.ts#L86). This allows Node.js integration but reduces security. Consider enabling sandbox with proper contextBridge APIs for production.

### Hot Module Replacement (HMR)
Development mode loads renderer from `ELECTRON_RENDERER_URL` for fast refresh. Production builds load from local HTML file.

### Platform-Specific Behavior
- macOS: App stays active when windows close (reactivate via dock)
- Windows/Linux: App quits when all windows close
- Linux-specific icon handling in window creation

## Project Structure
```
spec-desktop/
├── src/
│   ├── main/              # Electron 主进程
│   │   └── index.ts       # 主进程入口，管理后端子进程
│   ├── preload/           # 预加载脚本
│   │   └── index.ts       # contextBridge API
│   └── renderer/          # React 渲染进程
│       └── src/
│           ├── components/
│           ├── App.tsx
│           └── main.tsx
├── backend/               # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── utils/         # 工具函数
│   ├── requirements.txt   # Python 依赖
│   ├── build.py           # PyInstaller 打包脚本
│   └── README.md          # 后端文档
├── electron-builder.yml   # Electron 打包配置
├── package.json           # 前端依赖和脚本
└── CLAUDE.md              # 本文件
```

## Important Files

- [abstract-spec.md](abstract-spec.md): 需求说明书生成工具的功能规格（中文）
- [src/main/index.ts](src/main/index.ts): 主进程入口，包含后端服务启动/停止逻辑
- [backend/app/main.py](backend/app/main.py): FastAPI 后端入口
- [electron.vite.config.ts](electron.vite.config.ts): Vite 多进程构建配置
- [electron-builder.yml](electron-builder.yml): Electron 打包配置，包含后端资源打包设置
- [package.json](package.json): 前端依赖和构建脚本
- [backend/pyproject.toml](backend/pyproject.toml): Python 项目配置和依赖（uv 管理）
- [backend/requirements.txt](backend/requirements.txt): Python 依赖列表（可选，兼容性保留）

## Development Workflow

1. **首次设置**:
   ```bash
   # 安装前端依赖
   npm install

   # 安装后端依赖（使用 uv）
   cd backend
   uv sync
   cd ..
   ```

2. **开发**:
   ```bash
   npm run dev  # 自动启动前端和后端（后端通过 uv run main.py）
   ```

3. **后端依赖管理**:
   ```bash
   cd backend
   uv add package-name        # 添加依赖
   uv add --dev package-name  # 添加开发依赖
   uv sync                     # 同步依赖
   ```

4. **打包发布**:
   ```bash
   npm run build:mac     # 或 build:win / build:linux
   # 会自动：1) uv run build.py 打包后端 2) 构建前端 3) electron-builder 打包
   ```

## 功能实现状态

### ✅ 已完成功能

1. **Excel 解析服务** ([backend/app/services/excel_parser.py](backend/app/services/excel_parser.py))
   - 读取 Excel 文件（功能点拆分表）
   - 解析需求数据为结构化格式
   - 处理合并单元格和数据验证

2. **AI 服务集成** ([backend/app/services/ai_service.py](backend/app/services/ai_service.py))
   - 接入阿里云通义千问（Qwen）
   - 自动生成功能描述（100字）
   - 配置文件: [backend/.env](backend/.env)

3. **Mermaid 图表生成** ([src/main/mermaid.ts](src/main/mermaid.ts))
   - **本地化**：使用 `@mermaid-js/mermaid-cli`
   - 结构图（flowchart）: 显示功能模块关系
   - 流程图（sequenceDiagram）: 显示角色交互
   - 图片缓存机制

4. **Word 文档生成** ([backend/app/services/docx_writer.py](backend/app/services/docx_writer.py))
   - 使用 python-docx 生成 Word 文档
   - 插入标题、描述、图片
   - 自定义样式和格式

5. **完整工作流** ([backend/app/services/document_service.py](backend/app/services/document_service.py))
   - 步骤 1: 处理 Excel → 返回结构化数据
   - 步骤 2: 前端生成 Mermaid 图片（本地）
   - 步骤 3: 后端生成 Word 文档

6. **前端 UI** ([src/renderer/src/App.tsx](src/renderer/src/App.tsx))
   - 文件选择对话框
   - 实时进度显示
   - 状态提示和错误处理
   - 现代化界面设计

7. **IPC 通信** ([src/main/ipc-handlers.ts](src/main/ipc-handlers.ts))
   - 文件选择
   - Excel 处理
   - Mermaid 图片生成（本地）
   - Word 文档生成和保存

## 使用流程

1. **启动应用**: `npm run dev`
2. **点击"选择 Excel 文件"**
3. **选择包含"功能点拆分表"的 Excel 文件**
4. **自动处理**:
   - 解析 Excel → AI 生成描述 → 生成图表 → 输出 Word
5. **选择保存位置**
6. **完成！**

## 核心特性

- ✅ **0 服务器成本**: 完全本地化，Mermaid 图表在用户电脑生成
- ✅ **AI 驱动**: 使用阿里云通义千问生成功能描述
- ✅ **简化代码**: 去除冗余，保留核心业务逻辑
- ✅ **现代化架构**: Electron + React + Python + uv
- ✅ **完整工作流**: 从 Excel 到 Word 一键生成
