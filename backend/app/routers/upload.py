"""
文件上传相关路由
处理 Excel 文件上传
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import os
import shutil
from pathlib import Path

router = APIRouter()

# 临时文件存储目录
UPLOAD_DIR = Path("temp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/excel")
async def upload_excel(file: UploadFile = File(...)) -> Dict:
    """
    上传 Excel 文件

    Args:
        file: 上传的 Excel 文件

    Returns:
        包含文件ID和文件名的字典
    """
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持 Excel 文件格式 (.xlsx, .xls)")

    try:
        # 保存文件
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "filename": file.filename,
            "file_path": str(file_path),
            "message": "文件上传成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    finally:
        file.file.close()
