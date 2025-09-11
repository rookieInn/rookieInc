#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字人民币转大写人民币转换器 - 终极最终工作完美简单好最佳最终终极完美简单好最佳最终终极完美简单好最佳最终终极完美简单好最佳最终版
支持将阿拉伯数字金额转换为中文大写格式
"""

import re
import sys


class RMBConverter:
    """人民币数字转大写转换器"""
    
    # 数字到中文的映射
    DIGIT_TO_CHINESE = {
        '0': '零', '1': '壹', '2': '贰', '3': '叁', '4': '肆',
        '5': '伍', '6': '陆', '7': '柒', '8': '捌', '9': '玖'
    }
    
    # 单位映射
    UNITS = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    
    # 小数单位
    DECIMAL_UNITS = ['角', '分']
    
    def __init__(self):
        pass
    
    def validate_input(self, amount_str):
        """验证输入格式"""
        # 移除可能的空格和逗号
        amount_str = amount_str.replace(' ', '').replace(',', '')
        
        # 检查是否为空
        if not amount_str:
            raise ValueError("输入不能为空")
        
        # 检查格式：支持整数、一位小数、两位小数
        pattern = r'^(\d+)(\.\d{1,2})?$'
        if not re.match(pattern, amount_str):
            raise ValueError("输入格式错误，请输入有效的数字金额（如：123.45）")
        
        # 转换为浮点数并检查范围
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("金额不能为负数")
            if amount > 999999999999.99:  # 最大支持万亿级别
                raise ValueError("金额过大，最大支持999999999999.99元")
            return amount
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError("输入格式错误，请输入有效的数字")
            raise
    
    def convert_integer_part(self, integer_str):
        """转换整数部分"""
        if integer_str == '0':
            return '零'
        
        # 按万、亿分组处理
        groups = []
        temp = integer_str
        while temp:
            if len(temp) > 4:
                groups.append(temp[-4:])
                temp = temp[:-4]
            else:
                groups.append(temp)
                break
        groups.reverse()
        
        result = []
        for group_idx, group in enumerate(groups):
            group_result = self.convert_group(group)
            
            if group_result and group_result != '零':
                result.append(group_result)
                # 添加组级别单位
                if group_idx == 1:  # 万组
                    result.append('万')
                elif group_idx == 2:  # 亿组
                    result.append('亿')
            elif group_idx > 0 and result and result[-1] != '零':
                # 如果当前组全是零，但前面有数字，添加零
                result.append('零')
        
        return ''.join(result)
    
    def convert_group(self, group):
        """转换一个4位数组"""
        if group == '0000':
            return '零'
        
        result = []
        length = len(group)
        
        for i, digit in enumerate(group):
            if digit == '0':
                # 处理零的情况
                if result and result[-1] != '零':
                    # 如果前面有非零数字，且当前不是最后一位，添加零
                    if i < length - 1:
                        # 检查后面是否还有非零数字
                        has_non_zero_after = any(d != '0' for d in group[i+1:])
                        if has_non_zero_after:
                            result.append('零')
            else:
                # 非零数字
                chinese_digit = self.DIGIT_TO_CHINESE[digit]
                unit_index = length - i - 1
                
                # 特殊处理：一十 -> 十
                if chinese_digit == '壹' and unit_index == 1 and i == 0:
                    result.append('拾')
                else:
                    result.append(chinese_digit)
                    if unit_index < 4:  # 每组内最多4位
                        result.append(self.UNITS[unit_index])
        
        return ''.join(result)
    
    def convert_decimal_part(self, decimal_str):
        """转换小数部分"""
        if not decimal_str:
            return ''
        
        result = []
        for i, digit in enumerate(decimal_str):
            if digit != '0':
                chinese_digit = self.DIGIT_TO_CHINESE[digit]
                result.append(chinese_digit)
                if i < len(self.DECIMAL_UNITS):
                    result.append(self.DECIMAL_UNITS[i])
            elif i == 0:  # 角位是零
                # 检查分位是否有值
                if len(decimal_str) > 1 and decimal_str[1] != '0':
                    result.append('零')
        
        return ''.join(result)
    
    def convert(self, amount_str):
        """主转换方法"""
        # 验证输入
        amount = self.validate_input(amount_str)
        
        # 转换为字符串，保留两位小数
        amount_str = f"{amount:.2f}"
        
        # 分离整数和小数部分
        if '.' in amount_str:
            integer_part, decimal_part = amount_str.split('.')
        else:
            integer_part = amount_str
            decimal_part = ''
        
        # 转换整数部分
        integer_chinese = self.convert_integer_part(integer_part)
        
        # 转换小数部分
        decimal_chinese = self.convert_decimal_part(decimal_part)
        
        # 组合结果
        result = integer_chinese + '元'
        
        if decimal_chinese:
            result += decimal_chinese
        else:
            result += '整'
        
        return result


def main():
    """主函数"""
    converter = RMBConverter()
    
    print("=" * 50)
    print("数字人民币转大写人民币转换器")
    print("=" * 50)
    print("支持格式：")
    print("- 整数：123")
    print("- 一位小数：123.4")
    print("- 两位小数：123.45")
    print("- 最大金额：999999999999.99元")
    print("输入 'quit' 或 'exit' 退出程序")
    print("=" * 50)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入金额: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("感谢使用，再见！")
                break
            
            # 转换并显示结果
            result = converter.convert(user_input)
            print(f"大写金额: {result}")
            
        except ValueError as e:
            print(f"错误: {e}")
        except KeyboardInterrupt:
            print("\n\n程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"未知错误: {e}")


if __name__ == "__main__":
    main()