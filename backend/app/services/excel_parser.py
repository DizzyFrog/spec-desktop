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

        # 检查 Sheet 是否存在
        try:
            workbook = openpyxl.load_workbook(self.file_path, read_only=True)
            sheet_names = workbook.sheetnames
            workbook.close()

            if self.sheet_name not in sheet_names:
                raise ValueError(
                    f"未找到工作表 '{self.sheet_name}'。\n"
                    f"当前文件包含的工作表: {', '.join(sheet_names)}\n"
                    f"请确保 Excel 文件中包含名为 '{self.sheet_name}' 的工作表。"
                )
        except Exception as e:
            if "未找到工作表" in str(e):
                raise
            raise ValueError(f"无法读取 Excel 文件: {str(e)}")

        # 读取 Excel
        try:
            df = pd.read_excel(
                self.file_path,
                sheet_name=self.sheet_name,
                header=0,
                usecols=self.columns
            )
        except ValueError as e:
            # 列名不匹配
            if "Usecols" in str(e) or "not in columns" in str(e):
                # 读取实际的列名
                df_check = pd.read_excel(self.file_path, sheet_name=self.sheet_name, header=0, nrows=0)
                actual_columns = df_check.columns.tolist()
                missing_columns = [col for col in self.columns if col not in actual_columns]

                raise ValueError(
                    f"Excel 表头不正确！\n\n"
                    f"期望的列名: {', '.join(self.columns)}\n"
                    f"实际的列名: {', '.join(actual_columns)}\n"
                    f"缺少的列名: {', '.join(missing_columns)}\n\n"
                    f"请检查 '{self.sheet_name}' 工作表的表头是否正确。"
                )
            raise ValueError(f"读取 Excel 失败: {str(e)}")

        # 检查是否为空
        if df.empty:
            raise ValueError(
                f"工作表 '{self.sheet_name}' 没有数据！\n"
                f"请确保工作表中包含有效的需求数据。"
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

    def validate(self) -> Dict[str, Any]:
        """
        验证 Excel 数据

        Returns:
            {
                "valid": True/False,
                "errors": [
                    {
                        "type": "error_type",
                        "message": "错误消息",
                        "location": "具体位置",
                        "details": "详细信息"
                    }
                ],
                "warnings": [...]
            }
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        try:
            data = self.parse()
        except Exception as e:
            # 解析失败（Sheet不存在、列名错误等）
            result["valid"] = False
            result["errors"].append({
                "type": "parse_error",
                "message": "Excel 文件解析失败",
                "location": "文件结构",
                "details": str(e)
            })
            return result

        # 检查是否有数据
        if not data:
            result["valid"] = False
            result["errors"].append({
                "type": "no_data",
                "message": "没有找到有效的需求数据",
                "location": f"工作表 '{self.sheet_name}'",
                "details": "请确保工作表中包含 '功能用户需求'、'功能过程' 等必要数据。"
            })
            return result

        # 逐个检查功能需求
        for feature_name, feature_data in data.items():
            # 检查角色
            role = feature_data.get("角色", "")
            role_list = role.replace(',', '，').split("，")
            role_list = [r.strip() for r in role_list if r.strip()]

            if len(role_list) == 0:
                result["errors"].append({
                    "type": "missing_role",
                    "message": f"功能 '{feature_name}' 缺少角色信息",
                    "location": f"功能需求: {feature_name}",
                    "details": "每个功能需求必须指定至少一个角色。建议配置 3 个角色。"
                })
                result["valid"] = False
            elif len(role_list) < 3:
                result["warnings"].append({
                    "type": "insufficient_roles",
                    "message": f"功能 '{feature_name}' 的角色数量不足",
                    "location": f"功能需求: {feature_name}",
                    "details": f"当前角色: {role} (共 {len(role_list)} 个)\n建议配置 3 个角色以获得更好的流程图效果。"
                })
            elif len(role_list) > 3:
                result["warnings"].append({
                    "type": "too_many_roles",
                    "message": f"功能 '{feature_name}' 的角色数量过多",
                    "location": f"功能需求: {feature_name}",
                    "details": f"当前角色: {role} (共 {len(role_list)} 个)\n流程图只会使用前 3 个角色。"
                })

            # 检查功能过程
            process_count = sum(1 for k in feature_data.keys() if k != "角色")
            if process_count == 0:
                result["errors"].append({
                    "type": "no_process",
                    "message": f"功能 '{feature_name}' 没有功能过程",
                    "location": f"功能需求: {feature_name}",
                    "details": "每个功能需求必须包含至少一个功能过程。"
                })
                result["valid"] = False

            # 检查每个功能过程的子过程
            for process_name, process_data in feature_data.items():
                if process_name == "角色":
                    continue

                sub_processes, data_groups = process_data

                if len(sub_processes) == 0:
                    result["errors"].append({
                        "type": "no_subprocess",
                        "message": f"功能过程 '{process_name}' 没有子过程描述",
                        "location": f"功能需求: {feature_name} > 功能过程: {process_name}",
                        "details": "每个功能过程必须包含至少一个子过程描述。"
                    })
                    result["valid"] = False
                elif len(sub_processes) < 3:
                    result["warnings"].append({
                        "type": "insufficient_subprocess",
                        "message": f"功能过程 '{process_name}' 的子过程数量不足",
                        "location": f"功能需求: {feature_name} > 功能过程: {process_name}",
                        "details": f"当前子过程数: {len(sub_processes)} 个\n建议配置 3-5 个子过程以获得更好的流程图效果。\n系统会自动填充重复的子过程。"
                    })
                elif len(sub_processes) > 10:
                    result["warnings"].append({
                        "type": "too_many_subprocess",
                        "message": f"功能过程 '{process_name}' 的子过程数量过多",
                        "location": f"功能需求: {feature_name} > 功能过程: {process_name}",
                        "details": f"当前子过程数: {len(sub_processes)} 个\n建议将子过程数量控制在 3-10 个。\n流程图只会显示 3 个关键步骤（第1个、中间、最后一个），但 Word 文档会包含所有子过程。"
                    })
                elif len(sub_processes) > 5:
                    result["warnings"].append({
                        "type": "many_subprocess",
                        "message": f"功能过程 '{process_name}' 的子过程较多",
                        "location": f"功能需求: {feature_name} > 功能过程: {process_name}",
                        "details": f"当前子过程数: {len(sub_processes)} 个\n流程图只会显示 3 个关键步骤（第1个、中间、最后一个）。\n如果子过程较多，建议将其拆分为多个功能过程。"
                    })

        return result
