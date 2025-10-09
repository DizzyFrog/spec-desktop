from openai import OpenAI
from .myconfig import config_manager

class AIClient:
    def __init__(self):
        self._init_client()
    
    def _init_client(self):
        """使用最新配置初始化客户端"""
        config = config_manager.config
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        self.model = config["model"]

    def get_response_with_tongyi(self, prompt):
        # 确保每次使用最新配置
        self._init_client()
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': '你是软件需求工程师，负责需求分析'},
                {'role': 'user', 'content': prompt}
            ]
        )
        return completion.choices[0].message.content

aiclient = AIClient()
        
        