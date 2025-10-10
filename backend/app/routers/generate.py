"""
文档生成相关路由
处理需求文档生成、图表生成等逻辑
"""
import asyncio
import hashlib
import os
import subprocess
import tempfile
from typing import Any, Coroutine, Dict, List, Optional

from app.models.schemas import (GenerateMermaidImagesRequest, MermaidRequest,
                              ProcessExcelRequest, GenerateWordRequest)
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.document_service import document_service
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

router = APIRouter()

# --- 缓存和临时文件目录 ---
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'spec-desktop-backend')
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Mermaid CLI 并发控制 ---
# 限制同时运行的 mmdc 进程数量，避免 Puppeteer 资源竞争
MAX_CONCURRENT_MERMAID = 3
mermaid_semaphore = asyncio.Semaphore(MAX_CONCURRENT_MERMAID)


def _get_user_cache_dir(user_id: int) -> str:
    """
    获取用户专属的缓存目录
    每个用户有独立的缓存空间
    """
    user_cache_dir = os.path.join(TEMP_DIR, 'cache', f'user_{user_id}')
    os.makedirs(user_cache_dir, exist_ok=True)
    return user_cache_dir


async def _generate_png_from_mermaid_code(mermaid_code: str, user_id: int) -> str:
    """
    核心逻辑：接收 Mermaid 代码，生成 PNG 图片并返回路径。
    实现了基于内容哈希的缓存（按用户隔离）。
    使用信号量限制并发，避免 Puppeteer 资源竞争。
    """
    content_hash = hashlib.md5(mermaid_code.encode('utf-8')).hexdigest()
    user_cache_dir = _get_user_cache_dir(user_id)
    output_path = os.path.join(user_cache_dir, f"{content_hash}.png")

    if os.path.exists(output_path):
        print(f"✓ 使用缓存的 Mermaid 图片: {content_hash[:8]}.png")
        return output_path

    # 使用信号量限制并发执行
    async with mermaid_semaphore:
        # 双重检查：在获得信号量后再次检查缓存（可能其他任务已生成）
        if os.path.exists(output_path):
            print(f"✓ 使用缓存的 Mermaid 图片: {content_hash[:8]}.png")
            return output_path

        temp_mmd_path = ""
        try:
            print(f"⏳ 开始生成 Mermaid 图片: {content_hash[:8]}.png")
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mmd', encoding='utf-8') as temp_file:
                temp_mmd_path = temp_file.name
                temp_file.write(mermaid_code)

            command = ['mmdc', '-i', temp_mmd_path, '-o', output_path, '-b', 'transparent']

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

            if not os.path.exists(output_path):
                raise FileNotFoundError(f"mmdc 执行成功但未生成文件: {output_path}")

            print(f"✓ 图片生成成功: {content_hash[:8]}.png")
            return output_path

        except FileNotFoundError:
            print("错误: 'mmdc' command not found.")
            raise HTTPException(
                status_code=500,
                detail="服务器错误: 'mmdc' command not found. 请确保 Mermaid CLI 已在后端环境中全局安装。"
            )
        except subprocess.CalledProcessError as e:
            print(f"Mermaid CLI 执行失败. Code: {e.returncode}")
            stderr_str = e.stderr.decode('utf-8') if e.stderr else ''
            print(f"Stderr: {stderr_str}")
            raise HTTPException(status_code=500, detail=f"Mermaid 图表生成失败: {stderr_str}")
        finally:
            if temp_mmd_path and os.path.exists(temp_mmd_path):
                os.remove(temp_mmd_path)


@router.post("/mermaid")
async def generate_mermaid_diagram(
    request: MermaidRequest,
    current_user: User = Depends(get_current_user)
):
    """接收单段 Mermaid 代码，生成 PNG 图片并直接返回文件响应。需要登录。"""
    try:
        output_path = await _generate_png_from_mermaid_code(request.code, current_user.id)
        return FileResponse(output_path, media_type="image/png")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"生成 Mermaid 图表时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"生成图表时发生未知错误: {str(e)}")

# --- Mermaid 代码生成辅助函数 ---
def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def _get_structure_chart_code(feature_name: str, processes: List[str]) -> str:
    node_id = lambda text: 'N' + _hash_text(text)[:8]
    escape = lambda text: text.replace('"', '\\"')

    key_id = node_id(feature_name)
    escaped_key = escape(feature_name)
    content = f"    {key_id}[\"{escaped_key}\"]\n"

    for process in processes:
        process_id = node_id(process)
        escaped_process = escape(process)
        content += f"    {process_id}[\"{escaped_process}\"]\n"
        content += f"    {key_id} --> {process_id}\n"

    return f"flowchart TD\n{content}"

def _get_flow_chart_code(roles: List[str], processes: List[str]) -> str:
    escape = lambda text: text.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    a, b, c = (roles + ["", "", ""])[:3]  # Safely unpack
    step1 = processes[0] if processes else ""
    step2 = processes[len(processes) // 2] if processes else ""
    step3 = processes[-1] if processes else ""

    return f"""sequenceDiagram
    participant a as \"{escape(a)}\"
    participant b as \"{escape(b)}\"
    participant c as \"{escape(c)}\"

    a ->> b: \"{escape(step1)}\"
    b ->> c: \"{escape(step2)}\"
    b ->> a: \"{escape(step3)}\""""

@router.post("/mermaid-images")
async def generate_mermaid_images(
    request: GenerateMermaidImagesRequest,
    current_user: User = Depends(get_current_user)
):
    """接收章节数据，并行生成所有图表，返回路径映射。需要登录。"""
    tasks: Dict[str, Coroutine[Any, Any, str]] = {}

    for chapter in request.chapters:
        structure_key = f"structure_{chapter.name}"
        structure_code = _get_structure_chart_code(chapter.name, chapter.functions)
        tasks[structure_key] = _generate_png_from_mermaid_code(structure_code, current_user.id)

        if chapter.features:
            for feature in chapter.features:
                flow_key = f"flow_{feature.scenario}"
                flow_code = _get_flow_chart_code(feature.role, feature.process)
                tasks[flow_key] = _generate_png_from_mermaid_code(flow_code, current_user.id)

    print(f"开始并行生成 {len(tasks)} 张 Mermaid 图片...")
    
    try:
        results = await asyncio.gather(*tasks.values())
        
        image_mapping = {key: result for key, result in zip(tasks.keys(), results)}
        
        print("所有图片生成完成。")
        return {"code": 0, "data": {"imageMapping": image_mapping}}
    except Exception as e:
        print(f"并行生成 Mermaid 图片时出错: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"生成一张或多张图表时失败: {str(e)}")


@router.post("/process-excel")
async def process_excel(
    request: ProcessExcelRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """处理 Excel 文件，返回结构化数据。需要登录。"""
    try:
        print(f"📝 用户 {current_user.username} (ID: {current_user.id}) 正在处理 Excel 文件")
        result = await document_service.process_excel(request.file_path)
        # The result from the service is already in the desired format {"success": true, "chapters": [...]}
        # We just need to wrap it in the {code, data} structure.
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-word")
async def generate_word(
    request: GenerateWordRequest,
    current_user: User = Depends(get_current_user)
):
    """生成 Word 文档并返回文件。需要登录。"""
    try:
        print(f"📄 用户 {current_user.username} (ID: {current_user.id}) 正在生成 Word 文档")
        output_path = document_service.generate_word(
            request.chapters,
            request.image_mapping,
            request.output_filename
        )
        # 直接返回文件响应
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=request.output_filename or "需求说明书.docx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
