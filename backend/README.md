# 需求说明书生成工具 - 后端服务

基于 FastAPI 的后端服务，用于处理 Excel 解析、AI 内容生成和 Word 文档生成。

使用 **uv** 进行 Python 包管理，确保快速且可靠的依赖管理。

## 功能特性

- Excel 文件解析
- AI 驱动的内容生成
- Mermaid 图表语法生成
- Word 文档自动生成

## 前置要求

- Python >= 3.9
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

## 安装依赖

```bash
cd backend

# uv 会自动创建虚拟环境并安装依赖
uv sync
```

## 开发运行

```bash
# 使用 uv run 启动（推荐）
uv run main.py

# 或者激活虚拟环境后运行
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
python main.py
```

## 配置

1. 复制 `.env.example` 为 `.env`
2. 配置相应的 API Key 和参数

```bash
cp .env.example .env
```

## API 端点

### 健康检查
- `GET /` - 服务状态
- `GET /health` - 健康检查

### 文件上传
- `POST /api/upload/excel` - 上传 Excel 文件

### 文档生成
- `POST /api/generate/document` - 生成需求文档
- `POST /api/generate/mermaid` - 生成 Mermaid 图表

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── routers/             # API 路由
│   │   ├── upload.py        # 文件上传
│   │   └── generate.py      # 文档生成
│   ├── services/            # 业务逻辑
│   │   ├── excel_parser.py  # Excel 解析
│   │   ├── ai_service.py    # AI 服务
│   │   └── docx_writer.py   # Word 文档写入
│   ├── models/              # 数据模型
│   │   └── schemas.py       # Pydantic 模型
│   └── utils/               # 工具函数
├── requirements.txt         # Python 依赖
└── README.md
```

## 打包为可执行文件

使用 PyInstaller 通过 uv 打包：

```bash
# 使用 build.py 脚本自动打包
uv run build.py

# 打包后的文件位于 dist/spec-backend
```

## 依赖管理

### 添加新依赖

```bash
# 添加生产依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name
```

### 更新依赖

```bash
# 更新所有依赖
uv sync --upgrade

# 更新特定包
uv add package-name --upgrade
```

### 导出依赖（兼容 pip）

```bash
# 导出为 requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

## 注意事项

- 确保已安装 uv
- Python 版本要求 >= 3.9（推荐 3.13）
- 生产环境需要配置实际的 AI API Key
- 临时文件存储在 `temp/` 目录下
- uv 会自动创建和管理 `.venv/` 虚拟环境
