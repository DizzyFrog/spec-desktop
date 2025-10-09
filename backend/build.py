"""
使用 PyInstaller 打包后端为独立可执行文件的脚本
使用 uv 管理的 Python 环境
"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

def build_backend():
    """打包后端服务"""

    # 获取当前目录
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"
    dist_dir = backend_dir / "dist"
    build_dir = backend_dir / "build"

    # 清理旧的构建文件
    if dist_dir.exists():
        print("清理旧的构建文件...")
        shutil.rmtree(dist_dir)

    if build_dir.exists():
        shutil.rmtree(build_dir)

    # 构建命令
    output_name = "spec-backend"
    if platform.system() == "Windows":
        output_name += ".exe"

    print("开始打包后端服务（使用 uv 环境）...")

    # 使用 uv run 执行 pyinstaller
    cmd = [
        "uv", "run",
        "pyinstaller",
        "--name", "spec-backend",
        "--onefile",  # 打包成单个文件
        "--clean",
        "--noconfirm",
        # 添加数据文件
        f"--add-data={app_dir}{os.pathsep}app",
        # 隐藏控制台窗口（可选）
        # "--noconsole",
        # 主入口文件
        str(app_dir / "main.py")
    ]

    # 执行打包命令
    result = subprocess.run(cmd, cwd=backend_dir)

    if result.returncode == 0:
        print(f"\n✅ 打包成功!")
        print(f"可执行文件位置: {dist_dir / output_name}")
    else:
        print("\n❌ 打包失败!")
        sys.exit(1)

if __name__ == "__main__":
    build_backend()
