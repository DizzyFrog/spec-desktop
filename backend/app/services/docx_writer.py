"""
Word 文档写入服务
使用 python-docx 生成需求说明书
"""
from docx import Document
from docx.shared import Inches, Pt
from typing import Dict, Any, List
from pathlib import Path


class DocxWriter:
    """Word 文档写入器"""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.document = Document()

    def add_title(self, title: str, level: int = 0):
        """添加标题"""
        self.document.add_heading(title, level=level)

    def add_paragraph(self, text: str):
        """添加段落"""
        self.document.add_paragraph(text)

    def add_table(self, data: List[List[str]], headers: List[str] = None):
        """添加表格"""
        rows = len(data) + (1 if headers else 0)
        cols = len(data[0]) if data else 0

        table = self.document.add_table(rows=rows, cols=cols)
        table.style = 'Light Grid Accent 1'

        # 添加表头
        if headers:
            header_cells = table.rows[0].cells
            for i, header in enumerate(headers):
                header_cells[i].text = header

        # 添加数据
        start_row = 1 if headers else 0
        for i, row_data in enumerate(data):
            row_cells = table.rows[start_row + i].cells
            for j, cell_data in enumerate(row_data):
                row_cells[j].text = str(cell_data)

    def add_image(self, image_path: str, width: float = 6.0):
        """
        添加图片

        Args:
            image_path: 图片路径
            width: 图片宽度（英寸）
        """
        if Path(image_path).exists():
            self.document.add_picture(image_path, width=Inches(width))

    def save(self):
        """保存文档"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.document.save(self.output_path)

    def generate_document(self, data: Dict[str, Any], image_paths: List[str] = None):
        """
        生成完整文档

        Args:
            data: 文档数据
            image_paths: Mermaid 图表图片路径列表
        """
        # TODO: 根据数据结构生成完整文档
        self.add_title("需求说明书", 0)
        self.add_paragraph("本文档由系统自动生成")

        # 添加 Mermaid 图表
        if image_paths:
            self.add_title("系统流程图", 1)
            for img_path in image_paths:
                self.add_image(img_path)

        self.save()
