#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收件人信息自动识别解析器
Recipient Information Parser

自动识别收件人信息中的不同部分，包括：
- 姓名 (Name)
- 手机号码 (Phone Number)
- 地址 (Address)
- 邮政编码 (Postal Code)
- 省份/城市/区县 (Province/City/District)
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class RecipientInfo:
    """收件人信息数据结构"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    detailed_address: Optional[str] = None
    raw_text: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class RecipientParser:
    """收件人信息解析器"""
    
    def __init__(self):
        """初始化解析器，定义各种正则表达式模式"""
        # 中国手机号码正则表达式
        self.phone_pattern = re.compile(
            r'(?:\+?86[-\s]?)?1[3-9]\d{9}|1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}',
            re.IGNORECASE
        )
        
        # 中国邮政编码正则表达式
        self.postal_code_pattern = re.compile(r'\b\d{6}\b')
        
        # 中国省份/直辖市/自治区
        self.provinces = [
            '北京', '天津', '上海', '重庆', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
            '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东',
            '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏',
            '新疆', '台湾', '香港', '澳门'
        ]
        
        # 常见城市关键词
        self.city_keywords = [
            '市', '县', '区', '镇', '乡', '村', '街道', '路', '街', '巷', '弄', '号'
        ]
        
        # 地址关键词
        self.address_keywords = [
            '省', '市', '县', '区', '镇', '乡', '村', '街道', '路', '街', '巷', '弄', '号',
            '小区', '花园', '广场', '大厦', '中心', '商场', '超市', '银行', '学校', '医院'
        ]
        
        # 姓名模式（2-4个中文字符）
        self.name_pattern = re.compile(r'[\u4e00-\u9fff]{2,4}')
        
        # 构建省份匹配模式
        self.province_pattern = re.compile('|'.join(self.provinces))
        
        # 构建地址关键词匹配模式
        self.address_pattern = re.compile('|'.join(self.address_keywords))
    
    def extract_phone(self, text: str) -> Optional[str]:
        """提取手机号码"""
        match = self.phone_pattern.search(text)
        if match:
            # 清理格式，移除空格和连字符
            phone = re.sub(r'[-\s]', '', match.group())
            return phone
        return None
    
    def extract_postal_code(self, text: str) -> Optional[str]:
        """提取邮政编码"""
        match = self.postal_code_pattern.search(text)
        return match.group() if match else None
    
    def extract_province(self, text: str) -> Optional[str]:
        """提取省份"""
        match = self.province_pattern.search(text)
        return match.group() if match else None
    
    def extract_name(self, text: str) -> Optional[str]:
        """提取姓名（简单模式）"""
        # 移除电话号码和邮政编码
        clean_text = self.phone_pattern.sub('', text)
        clean_text = self.postal_code_pattern.sub('', clean_text)
        
        # 查找可能的姓名
        matches = self.name_pattern.findall(clean_text)
        if matches:
            # 过滤掉非姓名的词语
            exclude_keywords = ['信息', '收件', '地址', '电话', '手机', '姓名', '无姓名', '收件人', '联系人']
            for match in matches:
                if (2 <= len(match) <= 4 and 
                    not any(keyword in match for keyword in exclude_keywords) and
                    not any(char in match for char in ['省', '市', '区', '县', '镇', '乡', '村', '路', '街', '号'])):
                    return match
        return None
    
    def extract_address_components(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """提取地址组件：省份、城市、区县"""
        province = self.extract_province(text)
        
        # 移除省份后的文本
        remaining_text = text
        if province:
            remaining_text = remaining_text.replace(province, '')
        
        # 查找城市（包含"市"的词语）
        city_match = re.search(r'([^，,。\s]+市)', remaining_text)
        city = city_match.group(1) if city_match else None
        
        # 查找区县（包含"区"或"县"的词语）
        district_match = re.search(r'([^，,。\s]+(?:区|县))', remaining_text)
        district = district_match.group(1) if district_match else None
        
        # 清理区县名称，移除前面的"市"字
        if district and district.startswith('市'):
            district = district[1:]
        
        return province, city, district
    
    def extract_detailed_address(self, text: str) -> str:
        """提取详细地址"""
        # 移除已识别的组件
        clean_text = text
        
        # 移除电话号码
        clean_text = self.phone_pattern.sub('', clean_text)
        
        # 移除邮政编码
        clean_text = self.postal_code_pattern.sub('', clean_text)
        
        # 移除省份、城市、区县
        province, city, district = self.extract_address_components(text)
        if province:
            clean_text = clean_text.replace(province, '')
        if city:
            clean_text = clean_text.replace(city, '')
        if district:
            clean_text = clean_text.replace(district, '')
        
        # 移除姓名（如果存在）
        name = self.extract_name(text)
        if name:
            clean_text = clean_text.replace(name, '')
        
        # 清理多余的空格和标点
        clean_text = re.sub(r'[，,。\s]+', ' ', clean_text).strip()
        
        # 进一步清理，移除常见的非地址词汇
        exclude_words = ['收件人', '电话', '手机', '地址', '邮编', '：', ':', '，', ',', '。']
        for word in exclude_words:
            clean_text = clean_text.replace(word, '')
        
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text if clean_text else None
    
    def parse(self, text: str) -> RecipientInfo:
        """解析收件人信息"""
        if not text or not text.strip():
            return RecipientInfo(raw_text=text)
        
        # 清理输入文本
        clean_text = text.strip()
        
        # 提取各个组件
        name = self.extract_name(clean_text)
        phone = self.extract_phone(clean_text)
        postal_code = self.extract_postal_code(clean_text)
        province, city, district = self.extract_address_components(clean_text)
        detailed_address = self.extract_detailed_address(clean_text)
        
        # 构建完整地址
        address_parts = []
        if province:
            address_parts.append(province)
        if city:
            address_parts.append(city)
        if district:
            address_parts.append(district)
        if detailed_address:
            address_parts.append(detailed_address)
        
        full_address = ' '.join(address_parts) if address_parts else None
        
        return RecipientInfo(
            name=name,
            phone=phone,
            address=full_address,
            postal_code=postal_code,
            province=province,
            city=city,
            district=district,
            detailed_address=detailed_address,
            raw_text=text
        )
    
    def parse_multiple(self, texts: List[str]) -> List[RecipientInfo]:
        """批量解析多个收件人信息"""
        return [self.parse(text) for text in texts]
    
    def validate_phone(self, phone: str) -> bool:
        """验证手机号码格式"""
        return bool(self.phone_pattern.match(phone)) if phone else False
    
    def validate_postal_code(self, postal_code: str) -> bool:
        """验证邮政编码格式"""
        return bool(self.postal_code_pattern.match(postal_code)) if postal_code else False


def main():
    """主函数，演示用法"""
    parser = RecipientParser()
    
    # 测试用例
    test_cases = [
        "张三 13812345678 北京市朝阳区建国门外大街1号 100000",
        "李四 北京市海淀区中关村大街27号 13800138000",
        "王五 上海市浦东新区陆家嘴环路1000号 200120",
        "赵六 广东省深圳市南山区科技园 13888888888",
        "陈七 浙江省杭州市西湖区文三路259号 310012",
        "刘八 江苏省南京市鼓楼区中山路321号 210008 13999999999",
        "周九 四川省成都市锦江区春熙路123号 610021",
        "吴十 湖北省武汉市江汉区解放大道688号 430022 13777777777"
    ]
    
    print("收件人信息自动识别解析器演示")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case}")
        print("-" * 30)
        
        result = parser.parse(test_case)
        
        print(f"姓名: {result.name}")
        print(f"手机: {result.phone}")
        print(f"邮政编码: {result.postal_code}")
        print(f"省份: {result.province}")
        print(f"城市: {result.city}")
        print(f"区县: {result.district}")
        print(f"详细地址: {result.detailed_address}")
        print(f"完整地址: {result.address}")
        
        # 验证结果
        if result.phone:
            print(f"手机号验证: {'✓' if parser.validate_phone(result.phone) else '✗'}")
        if result.postal_code:
            print(f"邮编验证: {'✓' if parser.validate_postal_code(result.postal_code) else '✗'}")
        
        print(f"JSON格式:\n{result.to_json()}")


if __name__ == "__main__":
    main()