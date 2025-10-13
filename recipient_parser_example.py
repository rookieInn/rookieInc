#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收件人信息解析器使用示例
Recipient Information Parser Usage Examples
"""

from recipient_parser import RecipientParser, RecipientInfo
import json
import re
from typing import Optional


def basic_usage_example():
    """基本使用示例"""
    print("=" * 60)
    print("基本使用示例")
    print("=" * 60)
    
    # 创建解析器实例
    parser = RecipientParser()
    
    # 单个收件人信息解析
    text = "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
    result = parser.parse(text)
    
    print(f"原始文本: {text}")
    print(f"解析结果:")
    print(f"  姓名: {result.name}")
    print(f"  手机: {result.phone}")
    print(f"  省份: {result.province}")
    print(f"  区县: {result.district}")
    print(f"  详细地址: {result.detailed_address}")
    print(f"  邮政编码: {result.postal_code}")
    print(f"  完整地址: {result.address}")


def batch_processing_example():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("批量处理示例")
    print("=" * 60)
    
    parser = RecipientParser()
    
    # 批量收件人信息
    recipient_texts = [
        "李四 上海市浦东新区陆家嘴环路1000号 200120",
        "王五 13888888888 广东省深圳市南山区科技园 518000",
        "赵六 江苏省南京市鼓楼区中山路321号 210008",
        "陈七 浙江省杭州市西湖区文三路259号 310012 13777777777",
        "刘八 四川省成都市锦江区春熙路123号 610021"
    ]
    
    # 批量解析
    results = parser.parse_multiple(recipient_texts)
    
    print("批量解析结果:")
    for i, result in enumerate(results, 1):
        print(f"\n收件人 {i}:")
        print(f"  姓名: {result.name}")
        print(f"  手机: {result.phone}")
        print(f"  地址: {result.address}")
        print(f"  邮编: {result.postal_code}")


def validation_example():
    """验证功能示例"""
    print("\n" + "=" * 60)
    print("验证功能示例")
    print("=" * 60)
    
    parser = RecipientParser()
    
    # 测试手机号验证
    phone_numbers = ["13812345678", "13912345678", "12345678901", "1381234567"]
    print("手机号验证:")
    for phone in phone_numbers:
        is_valid = parser.validate_phone(phone)
        print(f"  {phone}: {'✓ 有效' if is_valid else '✗ 无效'}")
    
    # 测试邮政编码验证
    postal_codes = ["100000", "200120", "12345", "1234567"]
    print("\n邮政编码验证:")
    for code in postal_codes:
        is_valid = parser.validate_postal_code(code)
        print(f"  {code}: {'✓ 有效' if is_valid else '✗ 无效'}")


def json_output_example():
    """JSON输出示例"""
    print("\n" + "=" * 60)
    print("JSON输出示例")
    print("=" * 60)
    
    parser = RecipientParser()
    
    text = "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
    result = parser.parse(text)
    
    print(f"原始文本: {text}")
    print(f"JSON格式输出:")
    print(result.to_json())


def advanced_parsing_example():
    """高级解析示例"""
    print("\n" + "=" * 60)
    print("高级解析示例")
    print("=" * 60)
    
    parser = RecipientParser()
    
    # 复杂格式的收件人信息
    complex_cases = [
        "收件人：张三，电话：138-1234-5678，地址：北京市朝阳区建国门外大街1号国贸大厦A座1001室，邮编：100000",
        "李四 +86 138 0013 8000 上海市浦东新区陆家嘴环路1000号上海中心大厦 200120",
        "王五 广东省深圳市南山区科技园南区深圳湾科技生态园10栋A座 518000 13888888888",
        "赵六 江苏省南京市鼓楼区中山路321号南京国际金融中心 210008",
        "陈七 浙江省杭州市西湖区文三路259号昌地火炬大厦 310012 13777777777"
    ]
    
    for i, text in enumerate(complex_cases, 1):
        print(f"\n复杂案例 {i}:")
        print(f"原始文本: {text}")
        
        result = parser.parse(text)
        
        print(f"解析结果:")
        print(f"  姓名: {result.name}")
        print(f"  手机: {result.phone}")
        print(f"  省份: {result.province}")
        print(f"  城市: {result.city}")
        print(f"  区县: {result.district}")
        print(f"  详细地址: {result.detailed_address}")
        print(f"  邮政编码: {result.postal_code}")
        print(f"  完整地址: {result.address}")


def error_handling_example():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("错误处理示例")
    print("=" * 60)
    
    parser = RecipientParser()
    
    # 各种边界情况
    edge_cases = [
        "",  # 空字符串
        "   ",  # 空白字符串
        "无收件人信息",  # 无有效信息
        "123456789",  # 只有数字
        "张三",  # 只有姓名
        "13812345678",  # 只有手机号
        "北京市朝阳区",  # 只有地址
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"\n边界案例 {i}: '{text}'")
        result = parser.parse(text)
        
        if result.name or result.phone or result.address:
            print(f"  解析到信息: 姓名={result.name}, 手机={result.phone}, 地址={result.address}")
        else:
            print("  未解析到有效信息")


def custom_parser_example():
    """自定义解析器示例"""
    print("\n" + "=" * 60)
    print("自定义解析器示例")
    print("=" * 60)
    
    class CustomRecipientParser(RecipientParser):
        """自定义收件人解析器，添加特殊处理"""
        
        def extract_name(self, text: str) -> Optional[str]:
            """重写姓名提取，支持更多格式"""
            # 先调用父类方法
            name = super().extract_name(text)
            if name:
                return name
            
            # 尝试提取带称谓的姓名
            title_pattern = re.compile(r'(先生|女士|小姐|老师|经理|主任|总|博士|教授)\s*([\u4e00-\u9fff]{2,4})')
            match = title_pattern.search(text)
            if match:
                return match.group(2)
            
            return None
        
        def extract_company(self, text: str) -> Optional[str]:
            """提取公司名称"""
            company_pattern = re.compile(r'(有限公司|股份有限公司|集团|公司|企业|科技|贸易|实业)')
            match = company_pattern.search(text)
            if match:
                # 尝试提取公司名称
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 10)
                company_text = text[start:end]
                
                # 提取公司名称（简化处理）
                words = re.findall(r'[\u4e00-\u9fff]+', company_text)
                for word in words:
                    if len(word) >= 2 and '公司' in word or '集团' in word:
                        return word
            
            return None
    
    # 使用自定义解析器
    custom_parser = CustomRecipientParser()
    
    test_texts = [
        "张三先生 13812345678 北京市朝阳区",
        "李四女士 上海市浦东新区",
        "王五经理 广东省深圳市",
        "北京科技有限公司 赵六 13888888888 北京市海淀区"
    ]
    
    for text in test_texts:
        print(f"\n测试文本: {text}")
        result = custom_parser.parse(text)
        company = custom_parser.extract_company(text)
        
        print(f"  姓名: {result.name}")
        print(f"  手机: {result.phone}")
        print(f"  地址: {result.address}")
        print(f"  公司: {company}")


def main():
    """主函数"""
    print("收件人信息解析器使用示例")
    print("Recipient Information Parser Usage Examples")
    
    # 运行各种示例
    basic_usage_example()
    batch_processing_example()
    validation_example()
    json_output_example()
    advanced_parsing_example()
    error_handling_example()
    custom_parser_example()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()