from app.log import logger
import pandas as pd
import openpyxl
import json
from pathlib import Path
from .aiclient import aiclient
from .resolver import resolver
class SmarttoolService:
    
    
    def __init__(self):
        self.task_json_path = Path("web/public/resource/task.json")
        self.output_dir = Path("web/public/resource/file/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)  # 确保输出目录存在

    def process_task(self):
        try:
            logger.info("开始处理任务")

            # 解析
            # result = resolver.process_data()
            chapter_list = resolver.get_data_result()
            logger.info(f"获取到 {len(chapter_list)} 个章节")
            
            # 生成docx文档
            logger.info("开始生成Word文档")
            resolver.get_docx(chapter_list)
            logger.info("Word文档生成完成")
            
        except Exception as e:
            logger.error(f"处理任务时发生错误: {str(e)}")
            import traceback
            logger.error(f"完整错误栈: {traceback.format_exc()}")
            raise  # 重新抛出异常以便调用方知道失败了
        
        return None
    
    async def validateExcel(self, file):
        logger.info("开始验证Excel文件")

        filename = file.name
        logger.info(filename)
        workbook = openpyxl.load_workbook(file)
        sheet_names = workbook.sheetnames
        logger.info(sheet_names)
        
        # 构建配置字典
        config = {
            "excel_file_name": filename,
            "sheet_name": "功能点拆分表",
        }
        
        # 更新配置文件
        await self.update_config(config)
        
        # 重置 resolver 的 DataFrame 缓存
        resolver.df = None
        
        # 处理数据生成 JSON
        resolver.process_data()
        problems = resolver.check_info(resolver.output_path)
        logger.info(problems)
        if len(problems) > 0:
            raise ValueError(f"Excel文件验证失败: {problems}")
        

    async def update_config(self, config: dict):
        
        try:
            # 读取现有配置
            with open(self.task_json_path, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
            
            # 更新配置
            current_config.update(config)
            
            # 写入文件
            with open(self.task_json_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"配置文件更新成功: {config}")
        except Exception as e:
            logger.error(f"更新配置文件失败: {str(e)}")
            raise ValueError(f"更新配置文件失败: {str(e)}")
    

    async def get_task_progress(self):
        """获取任务处理进度"""
        try:
            progress = await resolver.get_progress()
            return progress
        except Exception as e:
            logger.error(f"获取进度信息失败: {str(e)}")
       
    

smarttool_service = SmarttoolService()  # 修正类名拼写错误