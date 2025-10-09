"""
Word 文档生成器 - 使用 python-docx 生成文档
"""
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, List, Any
from pathlib import Path
import os


class DocxWriter:
    """Word 文档生成器"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = Document()

    def add_title(self, title: str):
        """添加文档标题"""
        self.doc.add_heading(title, level=0)

    def add_chapter(self, chapter: Dict[str, Any]):
        """添加章节内容"""
        # 功能名称
        self.doc.add_heading(chapter.get('name', ''), level=1)

        # 功能概述
        self.doc.add_heading('功能概述', level=2)
        self.doc.add_paragraph(chapter.get('description', ''))

        # 结构图
        structure_image = chapter.get('structure_image', '')
        if structure_image and os.path.exists(structure_image):
            self.doc.add_heading('功能结构图', level=2)
            try:
                self.doc.add_picture(structure_image, width=Inches(6))
            except Exception as e:
                self.doc.add_paragraph(f"[图片加载失败: {e}]")

        # 功能过程详情
        features = chapter.get('features', [])
        if features:
            self.doc.add_heading('功能过程详情', level=2)
            for feature in features:
                scenario = feature.get('scenario', '')
                self.doc.add_heading(scenario, level=3)

                # 子过程
                processes = feature.get('process', [])
                if processes:
                    self.doc.add_paragraph('子过程:')
                    for i, process in enumerate(processes, 1):
                        self.doc.add_paragraph(f"{i}. {process}", style='List Number')

                # 流程图
                flow_chart = feature.get('flow_chart', '')
                if flow_chart and os.path.exists(flow_chart):
                    self.doc.add_paragraph('流程图:')
                    try:
                        self.doc.add_picture(flow_chart, width=Inches(5))
                    except Exception as e:
                        self.doc.add_paragraph(f"[流程图加载失败: {e}]")

                # 涉及数据
                input_data = feature.get('input', '')
                output_data = feature.get('output', '')
                if input_data or output_data:
                    self.doc.add_paragraph('涉及数据:')
                    if input_data:
                        self.doc.add_paragraph(f"• 输入: {input_data}", style='List Bullet')
                    if output_data:
                        self.doc.add_paragraph(f"• 输出: {output_data}", style='List Bullet')

        # 相关角色
        role = chapter.get('role', '')
        if role:
            self.doc.add_heading('相关角色', level=2)
            self.doc.add_paragraph(role)

        # 分页
        self.doc.add_page_break()

    def save(self) -> str:
        """保存文档"""
        self.doc.save(self.output_path)
        return self.output_path

    def create_document(self, chapters: List[Dict[str, Any]], image_mapping: Dict[str, str]) -> str:
        """
        创建 Word 文档

        Args:
            chapters: 章节数据列表
            image_mapping: 图片路径映射 {key: path}

        Returns:
            生成的文档路径
        """
        # 添加标题
        self.doc.add_heading('需求说明书', 0)

        # 遍历章节
        for chapter in chapters:
            feature_name = chapter.get('feature_name', '')
            description = chapter.get('description', '')
            processes = chapter.get('processes', [])
            roles = chapter.get('roles', '')

            # 功能名称
            self.doc.add_heading(feature_name, level=1)

            # 功能概述
            self.doc.add_heading('功能概述', level=2)
            self.doc.add_paragraph(description)

            # 结构图
            structure_key = f"{feature_name}_structure"
            if structure_key in image_mapping:
                self.doc.add_heading('功能结构图', level=2)
                try:
                    self.doc.add_picture(image_mapping[structure_key], width=Inches(6))
                except Exception as e:
                    self.doc.add_paragraph(f"[图片加载失败: {e}]")

            # 流程图
            flow_key = f"{feature_name}_flow"
            if flow_key in image_mapping:
                self.doc.add_heading('功能流程图', level=2)
                try:
                    self.doc.add_picture(image_mapping[flow_key], width=Inches(6))
                except Exception as e:
                    self.doc.add_paragraph(f"[图片加载失败: {e}]")

            # 功能过程详情
            self.doc.add_heading('功能过程详情', level=2)
            for process_name, process_data in processes.items():
                self.doc.add_heading(process_name, level=3)

                # 子过程
                if process_data and len(process_data) > 0:
                    subprocesses = process_data[0]
                    if subprocesses:
                        self.doc.add_paragraph('子过程:')
                        for i, subprocess in enumerate(subprocesses, 1):
                            self.doc.add_paragraph(f"{i}. {subprocess}", style='List Number')

                # 数据组
                if process_data and len(process_data) > 1:
                    data_groups = process_data[1]
                    if data_groups:
                        self.doc.add_paragraph('涉及数据:')
                        for data in data_groups:
                            self.doc.add_paragraph(f"• {data}", style='List Bullet')

            # 相关角色
            self.doc.add_heading('相关角色', level=2)
            self.doc.add_paragraph(roles)

            # 分页
            self.doc.add_page_break()

        # 保存文档
        self.doc.save(self.output_path)
        return self.output_path
