"""
内容安全过滤模块
检测敏感词和有害内容
"""

import re
from typing import List, Dict
from app.core.config import settings

class ContentFilter:
    """内容过滤器"""
    
    def __init__(self):
        # 敏感词列表（实际应用中应该从数据库或文件加载）
        self.sensitive_words = [
            "暴力", "色情", "赌博", "毒品", "政治敏感",
            "恐怖主义", "极端主义", "非法", "危险"
        ]
        
        # 危险活动关键词
        self.dangerous_activities = [
            "极限运动", "攀岩", "潜水", "跳伞", "蹦极",
            "野外探险", "无人区", "禁区"
        ]
        
        # 非法景点关键词
        self.illegal_places = [
            "私人领地", "军事禁区", "自然保护区核心区"
        ]
    
    async def is_safe(self, content: str) -> bool:
        """检查内容是否安全"""
        if not settings.enable_content_filtering:
            return True
        
        # 检查敏感词
        if settings.enable_sensitive_word_detection:
            if self._contains_sensitive_words(content):
                return False
        
        # 检查危险活动
        if self._contains_dangerous_activities(content):
            return False
        
        # 检查非法景点
        if self._contains_illegal_places(content):
            return False
        
        return True
    
    def _contains_sensitive_words(self, content: str) -> bool:
        """检查是否包含敏感词"""
        content_lower = content.lower()
        for word in self.sensitive_words:
            if word in content_lower:
                return True
        return False
    
    def _contains_dangerous_activities(self, content: str) -> bool:
        """检查是否包含危险活动"""
        content_lower = content.lower()
        for activity in self.dangerous_activities:
            if activity in content_lower:
                return True
        return False
    
    def _contains_illegal_places(self, content: str) -> bool:
        """检查是否包含非法景点"""
        content_lower = content.lower()
        for place in self.illegal_places:
            if place in content_lower:
                return True
        return False
    
    def get_filtered_content(self, content: str) -> str:
        """获取过滤后的内容"""
        filtered_content = content
        
        # 替换敏感词
        for word in self.sensitive_words:
            filtered_content = re.sub(
                word, 
                "*" * len(word), 
                filtered_content, 
                flags=re.IGNORECASE
            )
        
        return filtered_content
    
    def get_safety_report(self, content: str) -> Dict:
        """获取内容安全报告"""
        report = {
            "is_safe": True,
            "sensitive_words_found": [],
            "dangerous_activities_found": [],
            "illegal_places_found": [],
            "risk_level": "low"
        }
        
        content_lower = content.lower()
        
        # 检查敏感词
        for word in self.sensitive_words:
            if word in content_lower:
                report["sensitive_words_found"].append(word)
                report["is_safe"] = False
        
        # 检查危险活动
        for activity in self.dangerous_activities:
            if activity in content_lower:
                report["dangerous_activities_found"].append(activity)
                report["is_safe"] = False
        
        # 检查非法景点
        for place in self.illegal_places:
            if place in content_lower:
                report["illegal_places_found"].append(place)
                report["is_safe"] = False
        
        # 评估风险等级
        total_issues = (
            len(report["sensitive_words_found"]) +
            len(report["dangerous_activities_found"]) +
            len(report["illegal_places_found"])
        )
        
        if total_issues == 0:
            report["risk_level"] = "low"
        elif total_issues <= 2:
            report["risk_level"] = "medium"
        else:
            report["risk_level"] = "high"
        
        return report