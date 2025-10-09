from pathlib import Path
import json

class ConfigManager:
    def __init__(self):
        self.config_path = Path("web/public/resource/task.json")
        
    @property
    def config(self):
        """动态读取最新配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
            
        with open(self.config_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                raise ValueError("配置文件格式错误，请检查JSON语法")

config_manager = ConfigManager()