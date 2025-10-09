"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RequirementItem(BaseModel):
    """需求项模型"""
    id: str
    name: str
    description: str
    priority: Optional[str] = None
    status: Optional[str] = None


class RequirementSection(BaseModel):
    """需求章节模型"""
    title: str
    content: str
    requirements: List[RequirementItem] = []


class DocumentMetadata(BaseModel):
    """文档元数据"""
    project_name: str
    version: str
    author: Optional[str] = None
    date: Optional[str] = None


class GeneratedDocument(BaseModel):
    """生成的文档模型"""
    metadata: DocumentMetadata
    sections: List[RequirementSection]
    mermaid_diagrams: List[str] = []
