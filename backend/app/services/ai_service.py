"""
AI 服务集成 - 阿里云通义千问
简化版本，用于生成功能描述
"""
from typing import Optional
import os
from openai import OpenAI


class AIService:
    """AI 服务类 - 使用阿里云通义千问"""

    def __init__(self):
        self.base_url = os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.api_key = os.getenv("AI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "qwen-long")

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None

    def generate_description(self, feature_name: str, processes: list[str]) -> str:
        """
        生成功能描述

        Args:
            feature_name: 功能名称
            processes: 功能过程列表

        Returns:
            生成的功能描述（100字左右）
        """
        if not self.client:
            return f"这是关于{feature_name}的功能模块，主要包含{len(processes)}个功能过程。"

        prompt = f"""现在有一个功能需求:{feature_name},其功能过程有:{', '.join(processes)}。
你的任务：根据需求和功能过程，写出100字左右的功能概述"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': '你是软件需求工程师，负责需求分析'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"AI 调用失败: {e}")
            return f"这是关于{feature_name}的功能模块，主要包含{len(processes)}个功能过程。"


# 全局实例
ai_service = AIService()
