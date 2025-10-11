"""
文档生成服务 - 核心业务逻辑
整合 Excel 解析、AI 生成、Word 输出
"""
from pathlib import Path
from typing import Dict, List, Any
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .excel_parser import ExcelParser
from .ai_service import ai_service
from .docx_writer import DocxWriter


class DocumentService:
    """文档生成服务 - 简化版"""

    def __init__(self):
        self.upload_dir = Path("temp/uploads")
        self.output_dir = Path("temp/outputs")
        self.cache_dir = Path("temp/cache")

        # 确保目录存在
        for dir_path in [self.upload_dir, self.output_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.executor = ThreadPoolExecutor(max_workers=5)

    async def process_excel(self, file_path: str) -> Dict[str, Any]:
        """
        处理 Excel 文件，生成文档

        Args:
            file_path: Excel 文件路径
            mermaid_images: 从前端传来的 Mermaid 图片路径字典

        Returns:
            处理结果
        """
        try:
            # 1. 验证 Excel
            parser = ExcelParser(file_path)
            validation_result = parser.validate()

            # 如果验证失败，返回详细错误信息
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Excel 文件验证失败",
                    "validation": validation_result
                }

            # 如果有警告，也一并返回（但继续处理）
            if validation_result["warnings"]:
                print(f"⚠️  Excel 验证警告:")
                for warning in validation_result["warnings"]:
                    print(f"   - {warning['message']} ({warning['location']})")

            # 2. 解析 Excel
            data = parser.parse()

            # 3. 生成描述（使用 AI）
            chapters = []

            for feature_name, feature_data in data.items():
                role = feature_data.get("角色", "")
                functions = [k for k in feature_data.keys() if k != "角色"]

                # 使用 AI 生成描述
                loop = asyncio.get_event_loop()
                description = await loop.run_in_executor(
                    self.executor,
                    ai_service.generate_description,
                    feature_name,
                    functions
                )

                # 构建章节数据（图片路径由前端提供）
                chapter = {
                    "name": feature_name,
                    "description": description,
                    "role": role,
                    "functions": functions,
                    "features": []
                }

                # 处理每个功能过程
                for func_process, process_data in feature_data.items():
                    if func_process == "角色":
                        continue

                    sub_processes, data_groups = process_data

                    feature = {
                        "scenario": func_process,
                        "process": sub_processes,
                        "input": data_groups[0] if data_groups else "",
                        "output": data_groups[-1] if data_groups else "",
                        "role": role.split("，")
                    }
                    chapter["features"].append(feature)

                chapters.append(chapter)

            # 返回结构化数据，等待前端生成图片后再生成 Word
            result = {
                "success": True,
                "chapters": chapters
            }

            # 如果有警告，一并返回
            if validation_result.get("warnings"):
                result["warnings"] = validation_result["warnings"]

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_word(self, chapters: List[Dict], image_mapping: Dict[str, str], output_filename: str = "需求说明书.docx") -> str:
        """
        生成 Word 文档

        Args:
            chapters: 章节数据列表
            image_mapping: 图片映射 {"structure_key": "/path/to/image.png", "flow_key": "/path/to/image.png"}
            output_filename: 输出文件名

        Returns:
            生成的文档路径（绝对路径）
        """
        output_path = (self.output_dir / output_filename).resolve()
        writer = DocxWriter(str(output_path))

        writer.add_title("软件需求说明书")

        for chapter in chapters:
            # 添加结构图路径
            structure_key = f"structure_{chapter['name']}"
            chapter['structure_image'] = image_mapping.get(structure_key, '')

            # 为每个 feature 添加流程图路径
            for feature in chapter.get('features', []):
                flow_key = f"flow_{feature['scenario']}"
                feature['flow_chart'] = image_mapping.get(flow_key, '')

            writer.add_chapter(chapter)

        return writer.save()


# 全局实例
document_service = DocumentService()
