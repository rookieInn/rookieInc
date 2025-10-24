"""
个人地址模块 - 地址解析器
支持自动识别、解析和填充地址信息
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from address_models import AddressComponent, AddressParseResult, AddressType


class AddressParser:
    """地址解析器"""
    
    def __init__(self):
        # 中国行政区划正则表达式
        self.province_patterns = [
            r'([^省]+省)',
            r'([^市]+市)',
            r'([^自治区]+自治区)',
            r'([^特别行政区]+特别行政区)',
            r'(北京市|上海市|天津市|重庆市)'
        ]
        
        self.city_patterns = [
            r'([^市]+市)',
            r'([^县]+县)',
            r'([^区]+区)',
            r'([^州]+州)',
            r'([^盟]+盟)'
        ]
        
        self.district_patterns = [
            r'([^区]+区)',
            r'([^县]+县)',
            r'([^市]+市)',
            r'([^镇]+镇)',
            r'([^乡]+乡)',
            r'([^街道]+街道)'
        ]
        
        # 街道和门牌号模式
        self.street_patterns = [
            r'([^路]+路)',
            r'([^街]+街)',
            r'([^巷]+巷)',
            r'([^弄]+弄)',
            r'([^号]+号)',
            r'([^栋]+栋)',
            r'([^座]+座)',
            r'([^层]+层)',
            r'([^室]+室)',
            r'([^单元]+单元)'
        ]
        
        # 邮政编码模式
        self.postal_code_pattern = r'(\d{6})'
        
        # 电话号码模式
        self.phone_patterns = [
            r'(\d{11})',  # 手机号
            r'(\d{3,4}-\d{7,8})',  # 固定电话
            r'(\d{3,4}\d{7,8})'  # 无分隔符固定电话
        ]
    
    def parse_address(self, raw_address: str) -> AddressParseResult:
        """
        解析地址字符串
        
        Args:
            raw_address: 原始地址字符串
            
        Returns:
            AddressParseResult: 解析结果
        """
        if not raw_address or not raw_address.strip():
            return AddressParseResult(
                success=False,
                full_address="",
                components=AddressComponent(),
                confidence=0.0,
                errors=["地址不能为空"]
            )
        
        # 清理地址字符串
        cleaned_address = self._clean_address(raw_address)
        
        # 提取联系信息
        contact_info = self._extract_contact_info(cleaned_address)
        address_without_contact = contact_info['address']
        
        # 解析地址组件
        components = self._parse_components(address_without_contact)
        
        # 计算置信度
        confidence = self._calculate_confidence(components, address_without_contact)
        
        # 生成建议
        suggestions = self._generate_suggestions(components, address_without_contact)
        
        # 检查错误
        errors = self._validate_components(components)
        
        # 构建完整地址
        full_address = self._build_full_address(components)
        
        return AddressParseResult(
            success=len(errors) == 0 and confidence > 0.3,
            full_address=full_address,
            components=components,
            confidence=confidence,
            suggestions=suggestions,
            errors=errors
        )
    
    def _clean_address(self, address: str) -> str:
        """清理地址字符串"""
        # 移除多余空格
        cleaned = re.sub(r'\s+', ' ', address.strip())
        
        # 移除特殊字符但保留中文标点
        cleaned = re.sub(r'[^\u4e00-\u9fff\w\s\-\.\(\)（）]', '', cleaned)
        
        return cleaned
    
    def _extract_contact_info(self, address: str) -> Dict[str, str]:
        """提取联系信息"""
        contact_info = {
            'address': address,
            'name': None,
            'phone': None
        }
        
        # 提取电话号码
        for pattern in self.phone_patterns:
            match = re.search(pattern, address)
            if match:
                contact_info['phone'] = match.group(1)
                contact_info['address'] = address.replace(match.group(1), '').strip()
                break
        
        # 提取姓名（简单模式：地址开头的2-4个中文字符）
        name_match = re.match(r'^([\u4e00-\u9fff]{2,4})', contact_info['address'])
        if name_match:
            contact_info['name'] = name_match.group(1)
            contact_info['address'] = contact_info['address'][len(name_match.group(1)):].strip()
        
        return contact_info
    
    def _parse_components(self, address: str) -> AddressComponent:
        """解析地址组件"""
        components = AddressComponent()
        
        # 设置默认国家
        components.country = "中国"
        
        # 解析省份
        for pattern in self.province_patterns:
            match = re.search(pattern, address)
            if match:
                components.province = match.group(1)
                break
        
        # 解析城市
        for pattern in self.city_patterns:
            match = re.search(pattern, address)
            if match:
                components.city = match.group(1)
                break
        
        # 解析区县
        for pattern in self.district_patterns:
            match = re.search(pattern, address)
            if match:
                components.district = match.group(1)
                break
        
        # 解析街道和门牌号
        street_parts = []
        for pattern in self.street_patterns:
            matches = re.findall(pattern, address)
            street_parts.extend(matches)
        
        if street_parts:
            components.street = ' '.join(street_parts)
        
        # 解析邮政编码
        postal_match = re.search(self.postal_code_pattern, address)
        if postal_match:
            components.postal_code = postal_match.group(1)
        
        # 解析建筑物和房间信息
        building_match = re.search(r'([^栋座层室单元]+(?:栋|座|层|室|单元))', address)
        if building_match:
            components.building = building_match.group(1)
        
        return components
    
    def _calculate_confidence(self, components: AddressComponent, address: str) -> float:
        """计算解析置信度"""
        score = 0.0
        total_checks = 0
        
        # 检查省份
        if components.province:
            score += 0.3
        total_checks += 1
        
        # 检查城市
        if components.city:
            score += 0.3
        total_checks += 1
        
        # 检查区县
        if components.district:
            score += 0.2
        total_checks += 1
        
        # 检查街道
        if components.street:
            score += 0.2
        total_checks += 1
        
        # 检查地址长度（太短或太长都降低置信度）
        if 10 <= len(address) <= 100:
            score += 0.1
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _generate_suggestions(self, components: AddressComponent, address: str) -> List[str]:
        """生成地址建议"""
        suggestions = []
        
        if not components.province:
            suggestions.append("请添加省份信息，如：北京市、上海市、广东省等")
        
        if not components.city:
            suggestions.append("请添加城市信息，如：深圳市、广州市、杭州市等")
        
        if not components.district:
            suggestions.append("请添加区县信息，如：南山区、天河区、西湖区等")
        
        if not components.street:
            suggestions.append("请添加详细街道地址，如：科技园路123号")
        
        if len(address) < 10:
            suggestions.append("地址信息过于简单，请提供更详细的地址")
        
        return suggestions
    
    def _validate_components(self, components: AddressComponent) -> List[str]:
        """验证地址组件"""
        errors = []
        
        if not components.province and not components.city:
            errors.append("缺少省份或城市信息")
        
        if components.postal_code and not re.match(r'^\d{6}$', components.postal_code):
            errors.append("邮政编码格式不正确，应为6位数字")
        
        return errors
    
    def _build_full_address(self, components: AddressComponent) -> str:
        """构建完整地址"""
        parts = []
        
        if components.country:
            parts.append(components.country)
        
        if components.province:
            parts.append(components.province)
        
        if components.city:
            parts.append(components.city)
        
        if components.district:
            parts.append(components.district)
        
        if components.street:
            parts.append(components.street)
        
        if components.building:
            parts.append(components.building)
        
        if components.room:
            parts.append(components.room)
        
        return ' '.join(parts)
    
    def suggest_addresses(self, partial_address: str, limit: int = 5) -> List[str]:
        """
        根据部分地址提供建议
        
        Args:
            partial_address: 部分地址字符串
            limit: 建议数量限制
            
        Returns:
            List[str]: 地址建议列表
        """
        # 这里可以集成真实的地理编码服务
        # 目前提供一些示例建议
        suggestions = []
        
        if "北京" in partial_address:
            suggestions.extend([
                "北京市朝阳区建国门外大街1号",
                "北京市海淀区中关村大街27号",
                "北京市西城区金融大街35号"
            ])
        elif "上海" in partial_address:
            suggestions.extend([
                "上海市浦东新区陆家嘴环路1000号",
                "上海市黄浦区南京东路399号",
                "上海市静安区南京西路1376号"
            ])
        elif "深圳" in partial_address:
            suggestions.extend([
                "深圳市南山区科技园南区深南大道10000号",
                "深圳市福田区华强北路1号",
                "深圳市罗湖区人民南路2008号"
            ])
        
        return suggestions[:limit]
    
    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        地理编码：将地址转换为坐标
        
        Args:
            address: 地址字符串
            
        Returns:
            Optional[Dict[str, float]]: 坐标信息 {"lat": 纬度, "lng": 经度}
        """
        # 这里可以集成真实的地理编码服务（如高德地图、百度地图API）
        # 目前返回示例坐标
        return {
            "lat": 39.9042,
            "lng": 116.4074
        }
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        逆地理编码：将坐标转换为地址
        
        Args:
            lat: 纬度
            lng: 经度
            
        Returns:
            Optional[str]: 地址字符串
        """
        # 这里可以集成真实的逆地理编码服务
        # 目前返回示例地址
        return "北京市东城区天安门广场"


class AddressValidator:
    """地址验证器"""
    
    @staticmethod
    def validate_postal_code(postal_code: str) -> bool:
        """验证邮政编码"""
        return bool(re.match(r'^\d{6}$', postal_code))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证电话号码"""
        patterns = [
            r'^1[3-9]\d{9}$',  # 手机号
            r'^\d{3,4}-\d{7,8}$',  # 固定电话
            r'^\d{3,4}\d{7,8}$'  # 无分隔符固定电话
        ]
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @staticmethod
    def validate_address_format(address: str) -> bool:
        """验证地址格式"""
        if not address or len(address.strip()) < 5:
            return False
        
        # 检查是否包含必要的地理信息
        has_geographic_info = any(keyword in address for keyword in [
            '省', '市', '区', '县', '镇', '乡', '街道', '路', '街', '号'
        ])
        
        return has_geographic_info