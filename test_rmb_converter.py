#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字人民币转大写人民币转换器测试文件
"""

from rmb_converter import RMBConverter


def test_converter():
    """测试转换器功能"""
    converter = RMBConverter()
    
    # 测试用例
    test_cases = [
        # (输入, 期望输出)
        ("0", "零元整"),
        ("1", "壹元整"),
        ("10", "拾元整"),
        ("11", "拾壹元整"),
        ("100", "壹佰元整"),
        ("101", "壹佰零壹元整"),
        ("1000", "壹仟元整"),
        ("1001", "壹仟零壹元整"),
        ("1010", "壹仟零拾元整"),
        ("1100", "壹仟壹佰元整"),
        ("10000", "壹万元整"),
        ("10001", "壹万零壹元整"),
        ("10010", "壹万零拾元整"),
        ("10100", "壹万零壹佰元整"),
        ("11000", "壹万壹仟元整"),
        ("100000", "拾万元整"),
        ("1000000", "壹佰万元整"),
        ("10000000", "壹仟万元整"),
        ("100000000", "壹亿元整"),
        ("123456789", "壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖元整"),
        
        # 小数测试
        ("0.1", "零元壹角"),
        ("0.01", "零元零壹分"),
        ("0.11", "零元壹角壹分"),
        ("1.1", "壹元壹角"),
        ("1.01", "壹元零壹分"),
        ("1.11", "壹元壹角壹分"),
        ("10.1", "拾元壹角"),
        ("10.01", "拾元零壹分"),
        ("10.11", "拾元壹角壹分"),
        ("100.1", "壹佰元壹角"),
        ("100.01", "壹佰元零壹分"),
        ("100.11", "壹佰元壹角壹分"),
        ("123.45", "壹佰贰拾叁元肆角伍分"),
        ("1234.56", "壹仟贰佰叁拾肆元伍角陆分"),
        ("12345.67", "壹万贰仟叁佰肆拾伍元陆角柒分"),
        
        # 边界测试
        ("999999999999.99", "玖仟玖佰玖拾玖亿玖仟玖佰玖拾玖万玖仟玖佰玖拾玖元玖角玖分"),
    ]
    
    print("开始测试数字人民币转大写转换器...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected) in enumerate(test_cases, 1):
        try:
            result = converter.convert(input_val)
            if result == expected:
                print(f"✓ 测试 {i:2d}: {input_val:>15} -> {result}")
                passed += 1
            else:
                print(f"✗ 测试 {i:2d}: {input_val:>15} -> {result}")
                print(f"    期望: {expected}")
                failed += 1
        except Exception as e:
            print(f"✗ 测试 {i:2d}: {input_val:>15} -> 错误: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"测试完成: 通过 {passed} 个，失败 {failed} 个")
    
    # 测试错误输入
    print("\n测试错误输入处理...")
    error_cases = [
        "",
        "abc",
        "-123",
        "123.456",
        "1234567890123.45",  # 超出范围
    ]
    
    for error_input in error_cases:
        try:
            result = converter.convert(error_input)
            print(f"✗ 错误测试: '{error_input}' -> {result} (应该报错)")
        except ValueError as e:
            print(f"✓ 错误测试: '{error_input}' -> 正确捕获错误: {e}")
        except Exception as e:
            print(f"✗ 错误测试: '{error_input}' -> 意外错误: {e}")


if __name__ == "__main__":
    test_converter()