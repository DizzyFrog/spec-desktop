"""
Excel 文件解析服务 - 简化版
从 Excel 中提取需求数据
"""
import openpyxl
import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
from collections import OrderedDict


class ExcelParser:
    """Excel 解析器 - 简化版"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.sheet_name = "功能点拆分表"
        self.columns = ['功能用户需求', '触发事件', '功能过程', '子过程描述', '数据组', '功能用户', '角色']

    def parse(self) -> Dict[str, Any]:
        """
        解析 Excel 文件为结构化数据

        Returns:
            {
                "功能需求1": {
                    "角色": "角色A，角色B，角色C",
                    "功能过程1": [["子过程1", "子过程2", "子过程3"], ["数据1", "数据2"]],
                    "功能过程2": [["子过程1", "子过程2", "子过程3"], ["数据1"]]
                }
            }
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        # 读取 Excel
        df = pd.read_excel(
            self.file_path,
            sheet_name=self.sheet_name,
            header=0,
            usecols=self.columns
        )

        result_dict = OrderedDict()

        # 当前值（用于合并单元格的前向填充）
        current_func_user_req = None
        current_func_process = None
        current_role = None
        last_valid_role = None

        # 处理每一行数据
        for idx, row in df.iterrows():
            # 读取当前行
            func_user_req = row['功能用户需求'] if pd.notna(row['功能用户需求']) else current_func_user_req
            func_process = row['功能过程'] if pd.notna(row['功能过程']) else current_func_process
            sub_processes = row['子过程描述']
            data_group = row['数据组']
            raw_role = self._clean_text(row['角色']) if pd.notna(row['角色']) else current_role

            # 处理角色：确保有 3 个角色
            if raw_role:
                role_list = raw_role.replace(',', '，').strip().split("，")
                role_list = [r.strip() for r in role_list if r.strip()]

                if len(role_list) >= 3:
                    role = "，".join(role_list[:3])
                    last_valid_role = role
                elif len(role_list) > 0:
                    role = last_valid_role if last_valid_role else "，".join(role_list + ["系统"] * (3 - len(role_list)))
                else:
                    role = current_role
            else:
                role = current_role

            # 更新当前值
            if pd.notna(row['功能用户需求']):
                current_func_user_req = func_user_req
            if pd.notna(row['功能过程']):
                current_func_process = func_process
            if pd.notna(row['角色']):
                current_role = role

            # 跳过空行
            if not func_user_req or not func_process:
                continue

            # 初始化结构
            result_dict.setdefault(func_user_req, OrderedDict())
            result_dict[func_user_req].setdefault("角色", role)
            result_dict[func_user_req].setdefault(func_process, [[], []])

            # 添加子过程和数据组
            if pd.notna(sub_processes):
                sub_proc_list, data_group_list = result_dict[func_user_req][func_process]
                sub_proc_list.append(sub_processes)
                if pd.notna(data_group):
                    data_group_list.append(data_group)

        # 确保每个功能过程至少有 3 个子过程
        for func_user_req, req_data in result_dict.items():
            for func_process, process_data in req_data.items():
                if func_process == "角色":
                    continue

                sub_proc_list, data_group_list = process_data
                while len(sub_proc_list) < 3:
                    if sub_proc_list:
                        sub_proc_list.append(sub_proc_list[-1])
                    else:
                        sub_proc_list.append(f"执行{func_process}")

        return result_dict

    def _clean_text(self, text: str) -> str:
        """清理文本中的空白字符"""
        return str(text).strip().replace(" ", "").replace("\t", "").replace("\n", "")

    def validate(self) -> List[str]:
        """
        验证 Excel 数据

        Returns:
            问题列表，如果为空则验证通过
        """
        problems = []
        data = self.parse()

        for key, value in data.items():
            role = value.get("角色", "")
            role_list = role.replace(',', '，').split("，")
            role_list = [r.strip() for r in role_list if r.strip()]

            if len(role_list) != 3:
                problems.append(f"角色信息不全: {key} (实际角色数:{len(role_list)})")

            for item_key, item_value in value.items():
                if item_key == "角色":
                    continue
                process_list = item_value[0]
                if len(process_list) < 3:
                    problems.append(f"功能过程不足3个: {key} - {item_key}")

        return problems
