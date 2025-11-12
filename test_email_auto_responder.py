import tempfile
import unittest
from pathlib import Path

from email_auto_responder import (
    KeywordResponder,
    KeywordRule,
    ProcessedMessageStore,
    ResponseTemplate,
    format_template,
)


def make_rule(name, keywords, **kwargs):
    response = ResponseTemplate(subject="Re: {original_subject}", body="Auto reply")
    return KeywordRule(name=name, keywords=keywords, response=response, **kwargs)


class KeywordRuleTests(unittest.TestCase):
    def test_matches_ignore_case(self):
        rule = make_rule("greetings", ["hello", "你好"])
        self.assertEqual(rule.matches("HELLO there"), "hello")
        self.assertEqual(rule.matches("说你好吧"), "你好")

    def test_match_all(self):
        rule = make_rule("pricing", ["价格", "优惠"], match_all=True)
        self.assertEqual(rule.matches("关于价格和优惠政策"), "价格")
        self.assertIsNone(rule.matches("只提到价格"))


class KeywordResponderTests(unittest.TestCase):
    def test_returns_first_match(self):
        rule1 = make_rule("refund", ["退款"])
        rule2 = make_rule("support", ["帮助"])
        responder = KeywordResponder([rule1, rule2], None)
        template, rule, keyword = responder.match("需要退款", "麻烦退款")  # type: ignore
        self.assertEqual(rule.name, "refund")
        self.assertEqual(keyword, "退款")
        self.assertIn("Re:", template.subject)

    def test_falls_back_to_default(self):
        default = ResponseTemplate(subject="Re: {original_subject}", body="默认回复")
        responder = KeywordResponder([], default)
        template, rule, keyword = responder.match("无匹配", "内容")  # type: ignore
        self.assertIsNone(rule)
        self.assertEqual(keyword, "")
        self.assertEqual(template.body, "默认回复")


class FormatTemplateTests(unittest.TestCase):
    def test_missing_key_returns_empty_string(self):
        self.assertEqual(format_template("Value: {missing_key}", {"existing": "ok"}), "Value: ")


class ProcessedMessageStoreTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            store_path = Path(tmp_dir) / "store.json"
            store = ProcessedMessageStore(store_path)
            self.assertFalse(store.contains("123"))
            store.add("123")
            self.assertTrue(store.contains("123"))

            # Re-load from disk and ensure persistence
            store2 = ProcessedMessageStore(store_path)
            self.assertTrue(store2.contains("123"))


if __name__ == "__main__":
    unittest.main()
