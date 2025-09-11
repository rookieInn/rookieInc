#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字人民币转大写人民币转换器 - 终极最终工作完美简单好最佳最终终极完美简单版本
"""

def rmb_converter(amount):
    """
    将数字金额转换为中文大写人民币
    
    Args:
        amount: 数字金额（支持整数和浮点数）
    
    Returns:
        str: 中文大写人民币字符串
    """
    # 输入验证
    if not isinstance(amount, (int, float)):
        raise ValueError("输入必须是数字")
    
    if amount < 0:
        raise ValueError("金额不能为负数")
    
    if amount > 999999999999.99:
        raise ValueError("金额超出范围（最大999999999999.99元）")
    
    # 处理零
    if amount == 0:
        return "零元整"
    
    # 分离整数部分和小数部分
    integer_part = int(amount)
    decimal_part = round((amount - integer_part) * 100)
    
    # 数字到中文的映射
    digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    units = ['', '拾', '佰', '仟']
    big_units = ['', '万', '亿']
    
    def convert_group(num, group_name=''):
        """转换一个4位数组"""
        if num == 0:
            return ''
        
        result = ''
        num_str = str(num).zfill(4)
        
        for i, digit in enumerate(num_str):
            if digit != '0':
                # 特殊处理：如果第一位是1且是拾位，不显示"壹"
                if i == 1 and digit == '1' and len(result) == 0:
                    result += units[3-i]
                else:
                    result += digits[int(digit)] + units[3-i]
            elif result and result[-1] != '零':
                result += '零'
        
        # 清理多余的零
        result = result.replace('零零', '零')
        if result.endswith('零'):
            result = result[:-1]
        
        return result + group_name
    
    def convert_integer(num):
        """转换整数部分"""
        if num == 0:
            return '零'
        
        result = ''
        num_str = str(num)
        
        # 按4位分组
        groups = []
        while num_str:
            groups.append(num_str[-4:])
            num_str = num_str[:-4]
        
        groups.reverse()
        
        for i, group in enumerate(groups):
            group_num = int(group)
            if group_num > 0:
                group_result = convert_group(group_num)
                if group_result:
                    result += group_result + big_units[len(groups) - 1 - i]
        
        return result
    
    def convert_decimal(decimal):
        """转换小数部分"""
        if decimal == 0:
            return ''
        
        result = ''
        if decimal >= 10:
            result += digits[decimal // 10] + '角'
        if decimal % 10 > 0:
            result += digits[decimal % 10] + '分'
        elif decimal >= 10:
            # 如果只有角没有分，需要添加"零分"
            result += '零分'
        
        return result
    
    # 转换整数部分
    integer_result = convert_integer(integer_part)
    
    # 转换小数部分
    decimal_result = convert_decimal(decimal_part)
    
    # 组合结果
    if integer_result == '零':
        if decimal_result:
            return '零元' + decimal_result
        else:
            return '零元整'
    else:
        if decimal_result:
            return integer_result + '元' + decimal_result
        else:
            return integer_result + '元整'


def main():
    """主函数"""
    print("数字人民币转大写人民币转换器")
    print("=" * 50)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入金额（输入 'quit' 退出）: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("感谢使用！")
                break
            
            # 转换并显示结果
            amount = float(user_input)
            result = rmb_converter(amount)
            print(f"转换结果: {result}")
            
        except ValueError as e:
            print(f"输入错误: {e}")
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()