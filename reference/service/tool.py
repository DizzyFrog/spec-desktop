from .aiclient import aiclient
import uuid
import concurrent.futures
import subprocess
import json
from pathlib import Path
from app.log import logger


def get_ai_executor():
    """获取全局AI调用线程池"""
    global _ai_executor
    if _ai_executor is None:
        with _executor_lock:
            if _ai_executor is None:
                # 增加并发数到15，提升大数据量处理性能
                _ai_executor = concurrent.futures.ThreadPoolExecutor(max_workers=15, thread_name_prefix="ai-api")
    return _ai_executor

# 持久化缓存
_description_cache = {}
_description_cache_file = Path("web/public/resource/file/output/cache/descriptions.json")

def _load_description_cache():
    """加载描述缓存"""
    global _description_cache
    try:
        if _description_cache_file.exists():
            with open(_description_cache_file, 'r', encoding='utf-8') as f:
                _description_cache = json.load(f)
                logger.info(f"已加载 {len(_description_cache)} 个缓存描述")
    except Exception as e:
        logger.error(f"加载描述缓存失败: {str(e)}")
        _description_cache = {}

def _save_description_cache():
    """保存描述缓存"""
    try:
        _description_cache_file.parent.mkdir(parents=True, exist_ok=True)
        # 创建字典副本以避免并发修改时的迭代错误
        cache_copy = _description_cache.copy()
        with open(_description_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_copy, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存描述缓存失败: {str(e)}")

def get_description(key, functions):
    # 初始化缓存
    if not _description_cache:
        _load_description_cache()
    
    # 创建缓存键
    cache_key = f"{key}:{str(functions)}"
    
    # 检查缓存
    if cache_key in _description_cache:
        logger.info(f"使用缓存描述: {key}")
        return _description_cache[cache_key]
    
    problem = f'现在有一个功能需求:{key},其功能过程有:{functions} 。//你的任务有：1.根据需求和功能过程，写出100字左右的功能概述'
    
    # 添加重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            answer = aiclient.get_response_with_tongyi(problem)
            if answer and answer.strip():
                # 存入缓存并持久化
                _description_cache[cache_key] = answer
                _save_description_cache()
                logger.info(f"生成描述成功: {key}")
                return answer
        except Exception as e:
            logger.warning(f"生成描述失败 (尝试 {attempt + 1}/{max_retries}): {key}, 错误: {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避
    
    # 所有重试都失败，返回默认描述
    default_answer = f"这是关于{key}的功能模块，主要包含{len(functions)}个功能过程。"
    logger.error(f"生成描述失败，使用默认描述: {key}")
    _description_cache[cache_key] = default_answer
    _save_description_cache()
    return default_answer

def get_description_async(key, functions):
    """异步获取描述"""
    executor = get_ai_executor()
    future = executor.submit(get_description, key, functions)
    return future





import hashlib

def get_structure(key, functions):
    def escape_mermaid_text(text):
        """转义 Mermaid 特殊字符"""
        # 将文本用双引号包围以避免特殊字符问题
        return text.replace('"', '\\"')
    
    def generate_node_id(text):
        """生成唯一的节点ID"""
        # 使用哈希生成简短的节点ID
        import hashlib
        return 'N' + hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
    
    content = ""
    escaped_key = escape_mermaid_text(key)
    key_id = generate_node_id(key)
    
    # 定义根节点
    content += f'    {key_id}["{escaped_key}"]\n'
    
    for function in functions:
        escaped_function = escape_mermaid_text(function)
        function_id = generate_node_id(function)
        # 定义节点
        content += f'    {function_id}["{escaped_function}"]\n'
        # 定义连接
        content += f'    {key_id} --> {function_id}\n'
    
    mermaid_code = f'''
flowchart TD
{content}
'''
    
    # 基于内容生成哈希作为文件名，相同内容使用相同文件
    content_hash = hashlib.md5(mermaid_code.encode('utf-8')).hexdigest()
    filename = Path("web/public/resource/file/output/cache/images") / f"structure_{content_hash}.png"
    
    # 确保目录存在
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查文件是否已存在
    if filename.exists():
        logger.info(f"使用缓存结构图: {key}")
        # 返回虚拟 future，表示已完成
        from concurrent.futures import Future
        completed_future = Future()
        completed_future.set_result(None)
        return str(filename), completed_future
    
    future = generate_png_async(filename, mermaid_code)
    return str(filename), future  # 返回文件名和 future 对象


def get_flow_chart(role, process):
    def escape_mermaid_text(text):
        """转义 Mermaid 特殊字符"""
        # 转义引号和其他特殊字符
        return text.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    
    A,B,C = role
    # step1,step2,step3 = process
    step1 = process[0]
    step3 = process[-1]
    mid = len(process)//2
    step2 = process[mid]

    # 转义所有文本内容
    escaped_A = escape_mermaid_text(A)
    escaped_B = escape_mermaid_text(B)
    escaped_C = escape_mermaid_text(C)
    escaped_step1 = escape_mermaid_text(step1)
    escaped_step2 = escape_mermaid_text(step2)
    escaped_step3 = escape_mermaid_text(step3)

    mermaid_code = f'''sequenceDiagram
    participant a as "{escaped_A}"
    participant b as "{escaped_B}"
    participant c as "{escaped_C}"

    a ->> b: "{escaped_step1}"
    b ->> c: "{escaped_step2}"
    b ->> a: "{escaped_step3}"'''
    
    # 基于内容生成哈希作为文件名
    content_hash = hashlib.md5(mermaid_code.encode('utf-8')).hexdigest()
    filename = Path("web/public/resource/file/output/cache/images") / f"flow_{content_hash}.png"
    
    # 确保目录存在
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查文件是否已存在
    if filename.exists():
        logger.info(f"使用缓存流程图: {role}")
        # 返回虚拟 future，表示已完成
        from concurrent.futures import Future
        completed_future = Future()
        completed_future.set_result(None)
        return str(filename), completed_future
    
    future = generate_png_async(filename, mermaid_code)
    return str(filename), future  # 返回文件名和 future 对象


def gen_png(filename,mermaid):

    # 定义命令
    command = f'''
cat << EOF  | mmdc  -o {filename} --input -
{mermaid}
EOF
'''
    # 执行命令并捕获输出
    try:
        # 执行命令并捕获输出
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        print(output)
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，捕获错误信息
        print("命令执行失败:", e.output)
        


# 全局线程池，避免重复创建销毁线程池的开销
import threading
_png_executor = None
_ai_executor = None
_executor_lock = threading.Lock()

def get_png_executor():
    """获取全局PNG生成线程池"""
    global _png_executor
    if _png_executor is None:
        with _executor_lock:
            if _png_executor is None:
                _png_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix="mermaid-png")
    return _png_executor

def generate_png_async(filename, mermaid):
    """异步生成PNG，不等待结果"""
    executor = get_png_executor()
    # 提交任务但不等待结果，让调用者决定是否等待
    future = executor.submit(gen_png, filename, mermaid)
    return future  # 返回 future 对象，让调用者决定是否等待





