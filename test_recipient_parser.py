#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收件人信息解析器测试文件
Test file for recipient information parser
"""

import unittest
from recipient_parser import RecipientParser, RecipientInfo


class TestRecipientParser(unittest.TestCase):
    """收件人信息解析器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = RecipientParser()
    
    def test_phone_extraction(self):
        """测试手机号码提取"""
        test_cases = [
            ("张三 13812345678", "13812345678"),
            ("李四 138-1234-5678", "13812345678"),
            ("王五 138 1234 5678", "13812345678"),
            ("赵六 +86 138 1234 5678", "13812345678"),
            ("陈七 13812345678 北京市", "13812345678"),
            ("刘八 无手机号", None),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser.extract_phone(text)
                self.assertEqual(result, expected)
    
    def test_postal_code_extraction(self):
        """测试邮政编码提取"""
        test_cases = [
            ("北京市朝阳区 100000", "100000"),
            ("上海市浦东新区 200120", "200120"),
            ("广东省深圳市 518000", "518000"),
            ("无邮编信息", None),
            ("邮编 12345", None),  # 5位数字不是有效邮编
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser.extract_postal_code(text)
                self.assertEqual(result, expected)
    
    def test_province_extraction(self):
        """测试省份提取"""
        test_cases = [
            ("北京市朝阳区", "北京"),
            ("上海市浦东新区", "上海"),
            ("广东省深圳市", "广东"),
            ("江苏省南京市", "江苏"),
            ("无省份信息", None),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser.extract_province(text)
                self.assertEqual(result, expected)
    
    def test_name_extraction(self):
        """测试姓名提取"""
        test_cases = [
            ("张三 13812345678", "张三"),
            ("李四 北京市朝阳区", "李四"),
            ("王五 13812345678 北京市朝阳区", "王五"),
            ("赵六", "赵六"),
            ("陈七 13812345678 北京市朝阳区建国门外大街1号", "陈七"),
            ("无姓名信息", None),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.parser.extract_name(text)
                self.assertEqual(result, expected)
    
    def test_complete_parsing(self):
        """测试完整解析"""
        test_cases = [
            {
                "input": "张三 13812345678 北京市朝阳区建国门外大街1号 100000",
                "expected": {
                    "name": "张三",
                    "phone": "13812345678",
                    "province": "北京",
                    "city": None,
                    "district": "朝阳区",
                    "postal_code": "100000"
                }
            },
            {
                "input": "李四 北京市海淀区中关村大街27号 13800138000",
                "expected": {
                    "name": "李四",
                    "phone": "13800138000",
                    "province": "北京",
                    "city": None,
                    "district": "海淀区",
                    "postal_code": None
                }
            },
            {
                "input": "王五 上海市浦东新区陆家嘴环路1000号 200120",
                "expected": {
                    "name": "王五",
                    "phone": None,
                    "province": "上海",
                    "city": None,
                    "district": "浦东新区",
                    "postal_code": "200120"
                }
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case["input"]):
                result = self.parser.parse(case["input"])
                expected = case["expected"]
                
                self.assertEqual(result.name, expected["name"])
                self.assertEqual(result.phone, expected["phone"])
                self.assertEqual(result.province, expected["province"])
                self.assertEqual(result.city, expected["city"])
                self.assertEqual(result.district, expected["district"])
                self.assertEqual(result.postal_code, expected["postal_code"])
    
    def test_validation(self):
        """测试验证功能"""
        # 手机号验证
        self.assertTrue(self.parser.validate_phone("13812345678"))
        self.assertTrue(self.parser.validate_phone("13912345678"))
        self.assertFalse(self.parser.validate_phone("12345678901"))
        self.assertFalse(self.parser.validate_phone("1381234567"))
        self.assertFalse(self.parser.validate_phone(""))
        
        # 邮政编码验证
        self.assertTrue(self.parser.validate_postal_code("100000"))
        self.assertTrue(self.parser.validate_postal_code("200120"))
        self.assertFalse(self.parser.validate_postal_code("12345"))
        self.assertFalse(self.parser.validate_postal_code("1234567"))
        self.assertFalse(self.parser.validate_postal_code(""))
    
    def test_json_output(self):
        """测试JSON输出"""
        text = "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
        result = self.parser.parse(text)
        json_output = result.to_json()
        
        self.assertIsInstance(json_output, str)
        self.assertIn("张三", json_output)
        self.assertIn("13812345678", json_output)
        self.assertIn("北京", json_output)
    
    def test_multiple_parsing(self):
        """测试批量解析"""
        texts = [
            "张三 13812345678 北京市朝阳区",
            "李四 上海市浦东新区",
            "王五 广东省深圳市"
        ]
        
        results = self.parser.parse_multiple(texts)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "张三")
        self.assertEqual(results[1].name, "李四")
        self.assertEqual(results[2].name, "王五")


class TestRecipientInfo(unittest.TestCase):
    """收件人信息数据结构测试类"""
    
    def test_recipient_info_creation(self):
        """测试收件人信息对象创建"""
        info = RecipientInfo(
            name="张三",
            phone="13812345678",
            address="北京市朝阳区",
            postal_code="100000"
        )
        
        self.assertEqual(info.name, "张三")
        self.assertEqual(info.phone, "13812345678")
        self.assertEqual(info.address, "北京市朝阳区")
        self.assertEqual(info.postal_code, "100000")
    
    def test_recipient_info_to_dict(self):
        """测试转换为字典"""
        info = RecipientInfo(name="张三", phone="13812345678")
        result = info.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "张三")
        self.assertEqual(result["phone"], "13812345678")
        self.assertIsNone(result["address"])


def run_performance_test():
    """性能测试"""
    import time
    
    parser = RecipientParser()
    
    # 生成测试数据
    test_data = [
        "张三 13812345678 北京市朝阳区建国门外大街1号 100000",
        "李四 上海市浦东新区陆家嘴环路1000号 200120",
        "王五 广东省深圳市南山区科技园 518000",
        "赵六 江苏省南京市鼓楼区中山路321号 210008",
        "陈七 浙江省杭州市西湖区文三路259号 310012"
    ] * 100  # 500条测试数据
    
    # 测试解析性能
    start_time = time.time()
    results = parser.parse_multiple(test_data)
    end_time = time.time()
    
    print(f"性能测试结果:")
    print(f"解析 {len(test_data)} 条收件人信息")
    print(f"总耗时: {end_time - start_time:.4f} 秒")
    print(f"平均每条: {(end_time - start_time) / len(test_data) * 1000:.2f} 毫秒")
    print(f"成功解析: {len([r for r in results if r.name])} 条")


if __name__ == "__main__":
    # 运行单元测试
    print("运行收件人信息解析器测试...")
    unittest.main(verbosity=2)
    
    # 运行性能测试
    print("\n" + "="*50)
    run_performance_test()