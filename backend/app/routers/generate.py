"""
文档生成相关路由 - 简化版
处理需求文档生成逻辑
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from app.services.document_service import document_service

router = APIRouter()


class ProcessExcelRequest(BaseModel):
    """处理 Excel 请求"""
    file_path: str


class GenerateWordRequest(BaseModel):
    """生成 Word 请求"""
    chapters: List[Dict[str, Any]]
    image_mapping: Dict[str, str]
    output_filename: Optional[str] = "需求说明书.docx"


@router.post("/process-excel")
async def process_excel(request: ProcessExcelRequest) -> Dict:
    """
    步骤1: 处理 Excel 文件，返回结构化数据

    Args:
        request: 包含 Excel 文件路径

    Returns:
        {
            "success": true,
            "chapters": [
                {
                    "name": "功能需求名称",
                    "description": "AI 生成的描述",
                    "role": "角色A，角色B，角色C",
                    "functions": ["功能1", "功能2"],
                    "features": [...]
                }
            ]
        }
    """
    try:
        result = await document_service.process_excel(request.file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-word")
async def generate_word(request: GenerateWordRequest) -> Dict:
    """
    步骤2: 生成 Word 文档（前端已生成 Mermaid 图片）

    Args:
        request: 包含章节数据和图片映射

    Returns:
        {
            "success": true,
            "output_path": "/path/to/需求说明书.docx"
        }
    """
    try:
        output_path = document_service.generate_word(
            request.chapters,
            request.image_mapping,
            request.output_filename
        )
        return {
            "success": True,
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
