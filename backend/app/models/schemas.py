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


class MermaidRequest(BaseModel):
    """Mermaid 代码请求模型"""
    code: str

# --- Models for Mermaid Image Generation ---

class FeatureModel(BaseModel):
    scenario: str
    role: List[str]
    process: List[str]

class ChapterModel(BaseModel):
    name: str
    functions: List[str]
    features: Optional[List[FeatureModel]] = None
    # Allow other fields not explicitly defined
    class Config:
        extra = 'allow'

class GenerateMermaidImagesRequest(BaseModel):
    chapters: List[ChapterModel]


class ProcessExcelRequest(BaseModel):
    """处理 Excel 请求"""
    file_path: str


class GenerateWordRequest(BaseModel):
    """生成 Word 请求"""
    chapters: List[Dict[str, Any]]
    image_mapping: Dict[str, str]
    output_filename: Optional[str] = "需求说明书.docx"
