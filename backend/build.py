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

    # 使用环境变量判断是否使用 onedir 模式（CI 环境下更快）
    use_onedir = os.environ.get("PYINSTALLER_ONEDIR", "false").lower() == "true"

    # 使用 uv run 执行 pyinstaller
    cmd = [
        "uv", "run",
        "pyinstaller",
        "--name", "spec-backend",
        "--onedir" if use_onedir else "--onefile",  # CI 环境用 onedir 加速
        "--clean",
        "--noconfirm",
        # 排除不需要的模块以减少体积和加速打包
        "--exclude-module", "pytest",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        # 注意：不排除 numpy，因为 pandas 依赖它
        # "--exclude-module", "numpy",
        "--exclude-module", "PIL",
        # 添加数据文件
        f"--add-data={app_dir}{os.pathsep}app",
        # 隐藏控制台窗口（可选）
        # "--noconsole",
        # 主入口文件
        str(app_dir / "main.py")
    ]

    print(f"打包模式: {'onedir' if use_onedir else 'onefile'}")

    # 执行打包命令
    result = subprocess.run(cmd, cwd=backend_dir, env={**os.environ, 'PYTHONOPTIMIZE': '1'})

    if result.returncode == 0:
        # 确保 dist 目录在 backend 下
        expected_dist = backend_dir / "dist"
        if not expected_dist.exists():
            expected_dist.mkdir(parents=True)

        print(f"\n✅ 打包成功!")
        print(f"可执行文件位置: {expected_dist / output_name}")
    else:
        print("\n❌ 打包失败!")
        sys.exit(1)

if __name__ == "__main__":
    build_backend()
