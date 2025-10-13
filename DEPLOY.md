# 部署说明

本文档提供了本项目的部署说明。项目采用前后端分离的架构，需要分别部署。

## 环境准备

在开始部署之前，请确保您的环境中已经安装了以下软件和工具：

- **后端**: Python (>= 3.9), uv
- **前端**: Node.js, pnpm

## 后端部署

1. 进入后端项目目录：

   ```bash
   cd backend
   ```
2. 安装依赖：

   ```bash
   uv sync
   ```

   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

3. 执行构建（如果需要）：

   ```bash
   uv run mian.py
   ```

   构建完成后，会在 `dist` 目录下生成可部署的文件。
4. 运行应用：
   您可以将项目文件部署到您的服务器上。在生产环境中，推荐使用 Gunicorn 或 uvicorn 配合 systemd 等进程管理工具来运行应用。

   同时，请根据 `.env.example` 文件创建并配置您的 `.env` 文件，以设置数据库连接、密钥等环境变量。

## 前端部署

1. 进入前端项目目录：

   ```bash
   cd frontend
   ```
2. 安装依赖：

   ```bash
   pnpm install
   ```
3. 执行构建：

   ```bash
   pnpm dev:antd
   ```
   该命令会专门构建 `web-antd` 应用，并在 `apps/web-antd/dist` 目录下生成用于生产环境的静态文件（HTML, CSS, JavaScript）。
4. 部署静态文件：
   您需要将构建生成的静态文件部署到像 Nginx、Apache 这样的 Web 服务器上，或者使用 Vercel、Netlify 等静态网站托管服务。

   **注意**：在部署后，请确保前端应用中的 API 请求地址已正确配置，指向您部署的后端服务地址。
