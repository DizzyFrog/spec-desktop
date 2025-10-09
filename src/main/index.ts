import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

// 后端服务进程
let backendProcess: ChildProcess | null = null
const BACKEND_PORT = 8000

/**
 * 启动 Python 后端服务
 */
function startBackendServer(): Promise<void> {
  return new Promise((resolve, reject) => {
    console.log('正在启动后端服务...')

    // 确定后端路径
    const backendPath = is.dev
      ? join(__dirname, '../../backend')
      : join(process.resourcesPath, 'backend')

    // 确定 Python 命令和参数
    // 开发环境：使用 uv run 启动
    // 生产环境：运行打包后的可执行文件
    const pythonCmd = is.dev ? 'uv' : join(process.resourcesPath, 'backend', 'spec-backend')
    const args = is.dev ? ['run', 'main.py'] : []

    // 启动后端进程
    backendProcess = spawn(pythonCmd, args, {
      cwd: backendPath,
      env: { ...process.env },
      shell: true
    })

    backendProcess.stdout?.on('data', (data) => {
      console.log(`[Backend] ${data.toString()}`)
      // 检测到服务启动成功
      if (data.toString().includes('Uvicorn running on') || data.toString().includes('Application startup complete')) {
        resolve()
      }
    })

    backendProcess.stderr?.on('data', (data) => {
      console.error(`[Backend Error] ${data.toString()}`)
    })

    backendProcess.on('error', (error) => {
      console.error('后端启动失败:', error)
      reject(error)
    })

    backendProcess.on('close', (code) => {
      console.log(`后端进程退出，代码: ${code}`)
      backendProcess = null
    })

    // 设置超时，如果 5 秒内没有成功信号也认为启动成功
    setTimeout(() => {
      if (backendProcess) {
        resolve()
      }
    }, 5000)
  })
}

/**
 * 停止后端服务
 */
function stopBackendServer(): void {
  if (backendProcess) {
    console.log('正在停止后端服务...')
    backendProcess.kill()
    backendProcess = null
  }
}

function createWindow(): void {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(async () => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // 启动后端服务
  try {
    await startBackendServer()
    console.log(`后端服务已启动，运行在 http://127.0.0.1:${BACKEND_PORT}`)
  } catch (error) {
    console.error('后端服务启动失败:', error)
  }

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopBackendServer()
    app.quit()
  }
})

// 应用退出前停止后端服务
app.on('before-quit', () => {
  stopBackendServer()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
