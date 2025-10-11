"""
测试 AI 服务是否正常工作
"""
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

print("=" * 60)
print("环境变量检查:")
print("=" * 60)
print(f"AI_API_KEY: {os.getenv('AI_API_KEY', 'NOT FOUND')[:20]}..." if os.getenv('AI_API_KEY') else "AI_API_KEY: NOT FOUND")
print(f"AI_MODEL: {os.getenv('AI_MODEL', 'NOT FOUND')}")
print(f"AI_BASE_URL: {os.getenv('AI_BASE_URL', 'NOT FOUND')}")
print()

# 导入 AI 服务
from app.services.ai_service import ai_service

print("=" * 60)
print("AI 服务测试:")
print("=" * 60)

# 测试生成描述
test_feature = "用户登录"
test_processes = ["用户输入账号密码", "系统验证", "登录成功"]

print(f"\n测试功能: {test_feature}")
print(f"功能过程: {test_processes}")
print("\n生成中...\n")

description = ai_service.generate_description(test_feature, test_processes)

print("=" * 60)
print("生成结果:")
print("=" * 60)
print(description)
print()
