import os
import unittest

from app.services.ai_service import AIService


class FakeCompletionChoice:
    def __init__(self, content: str):
        class Msg:
            def __init__(self, c):
                self.content = c
        self.message = Msg(content)


class FakeCompletionsAPI:
    def __init__(self, response_text: str):
        self._resp = response_text

    def create(self, model, messages):
        class Completion:
            def __init__(self, text):
                self.choices = [FakeCompletionChoice(text)]
        # simple echo behavior for verification
        return Completion(self._resp)


class FakeOpenAIClient:
    def __init__(self, response_text: str = "ok"):
        self.chat = type("Chat", (), {"completions": FakeCompletionsAPI(response_text)})()


class TestAIService(unittest.TestCase):
    def setUp(self):
        # Ensure no real API key interferes
        os.environ.pop("AI_API_KEY", None)

    def test_fallback_without_client(self):
        ai = AIService()
        # Force client None
        ai.client = None
        text = ai.generate_description("用户管理", ["创建用户", "编辑用户"])
        self.assertIn("这是关于用户管理的功能模块", text)
        self.assertIn("主要包含2个功能过程", text)

    def test_generate_with_mock_client(self):
        ai = AIService()
        # Inject fake client
        ai.client = FakeOpenAIClient("生成的功能概述文本")
        desc = ai.generate_description("订单处理", ["下单", "支付", "发货"])
        self.assertEqual(desc, "生成的功能概述文本")


if __name__ == "__main__":
    unittest.main()
