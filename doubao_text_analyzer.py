#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包API文字分析和关键字提取工具
"""

import os
import json
import time
import requests
import logging
from typing import Optional, Dict, Any, List
import configparser
from datetime import datetime


class DoubaoTextAnalyzer:
    """豆包API文字分析客户端"""
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化豆包API客户端
        
        Args:
            api_key: 豆包API密钥
            base_url: API基础URL，默认为官方地址
        """
        self.api_key = api_key
        self.base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('doubao_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_text(self, text: str, analysis_type: str = "keywords") -> Optional[Dict[str, Any]]:
        """
        分析文字内容
        
        Args:
            text: 要分析的文字内容
            analysis_type: 分析类型 (keywords, sentiment, summary, entities)
        
        Returns:
            分析结果字典
        """
        try:
            if not text.strip():
                self.logger.warning("输入文字为空")
                return None
            
            # 构建提示词
            prompt = self._build_prompt(text, analysis_type)
            
            # 调用API
            response = self._call_doubao_api(prompt)
            
            if response:
                return self._parse_response(response, analysis_type)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"分析文字时出错: {e}")
            return None
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        提取关键字
        
        Args:
            text: 要分析的文字
            max_keywords: 最大关键字数量
        
        Returns:
            关键字列表，每个关键字包含词、权重、类型等信息
        """
        try:
            prompt = f"""
请分析以下文字并提取关键字，要求：
1. 提取{max_keywords}个最重要的关键字
2. 按重要性排序
3. 为每个关键字提供权重分数(0-1)
4. 标注关键字类型(名词、动词、形容词等)
5. 返回JSON格式

文字内容：
{text}

请返回JSON格式：
{{
    "keywords": [
        {{
            "word": "关键字",
            "weight": 0.95,
            "type": "名词",
            "description": "关键字描述"
        }}
    ]
}}
"""
            
            response = self._call_doubao_api(prompt)
            
            if response:
                return self._parse_keywords_response(response)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"提取关键字时出错: {e}")
            return None
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        情感分析
        
        Args:
            text: 要分析的文字
        
        Returns:
            情感分析结果
        """
        try:
            prompt = f"""
请对以下文字进行情感分析，要求：
1. 判断情感倾向(积极、消极、中性)
2. 给出情感强度分数(0-1)
3. 分析主要情感因素
4. 返回JSON格式

文字内容：
{text}

请返回JSON格式：
{{
    "sentiment": "积极/消极/中性",
    "score": 0.85,
    "confidence": 0.92,
    "factors": ["因素1", "因素2"],
    "summary": "情感分析总结"
}}
"""
            
            response = self._call_doubao_api(prompt)
            
            if response:
                return self._parse_sentiment_response(response)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"情感分析时出错: {e}")
            return None
    
    def generate_summary(self, text: str, max_length: int = 200) -> Optional[str]:
        """
        生成文字摘要
        
        Args:
            text: 要摘要的文字
            max_length: 摘要最大长度
        
        Returns:
            文字摘要
        """
        try:
            prompt = f"""
请为以下文字生成摘要，要求：
1. 摘要长度不超过{max_length}字
2. 保留核心信息和关键观点
3. 语言简洁明了
4. 只返回摘要内容，不要其他说明

文字内容：
{text}
"""
            
            response = self._call_doubao_api(prompt)
            
            if response:
                return self._parse_summary_response(response)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"生成摘要时出错: {e}")
            return None
    
    def extract_entities(self, text: str) -> Optional[Dict[str, List[str]]]:
        """
        实体识别
        
        Args:
            text: 要分析的文字
        
        Returns:
            实体识别结果，按类型分组
        """
        try:
            prompt = f"""
请识别以下文字中的实体，要求：
1. 识别人名、地名、机构名、时间、数字等实体
2. 按实体类型分组
3. 返回JSON格式

文字内容：
{text}

请返回JSON格式：
{{
    "person": ["人名1", "人名2"],
    "location": ["地名1", "地名2"],
    "organization": ["机构1", "机构2"],
    "time": ["时间1", "时间2"],
    "number": ["数字1", "数字2"],
    "other": ["其他实体"]
}}
"""
            
            response = self._call_doubao_api(prompt)
            
            if response:
                return self._parse_entities_response(response)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"实体识别时出错: {e}")
            return None
    
    def _build_prompt(self, text: str, analysis_type: str) -> str:
        """构建分析提示词"""
        prompts = {
            "keywords": f"请分析以下文字并提取关键字：\n{text}",
            "sentiment": f"请分析以下文字的情感倾向：\n{text}",
            "summary": f"请为以下文字生成摘要：\n{text}",
            "entities": f"请识别以下文字中的实体：\n{text}"
        }
        return prompts.get(analysis_type, f"请分析以下文字：\n{text}")
    
    def _call_doubao_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用豆包API"""
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": "ep-20241220102345-xxxxx",  # 需要替换为实际的模型ID
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("API调用成功")
                return result
            else:
                self.logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"调用API时出错: {e}")
            return None
    
    def _parse_response(self, response: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """解析API响应"""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "analysis_type": analysis_type,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "raw_response": response
            }
            
        except Exception as e:
            self.logger.error(f"解析响应时出错: {e}")
            return {"error": str(e)}
    
    def _parse_keywords_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析关键字提取响应"""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content
            
            result = json.loads(json_str)
            return result.get("keywords", [])
            
        except Exception as e:
            self.logger.error(f"解析关键字响应时出错: {e}")
            return []
    
    def _parse_sentiment_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析情感分析响应"""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content
            
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"解析情感分析响应时出错: {e}")
            return {"error": str(e)}
    
    def _parse_summary_response(self, response: Dict[str, Any]) -> str:
        """解析摘要响应"""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"解析摘要响应时出错: {e}")
            return ""
    
    def _parse_entities_response(self, response: Dict[str, Any]) -> Dict[str, List[str]]:
        """解析实体识别响应"""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析JSON
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content
            
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"解析实体识别响应时出错: {e}")
            return {}


class DoubaoTextAnalyzerConfig:
    """豆包文字分析器配置管理"""
    
    def __init__(self, config_file: str = "doubao_config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        self.config['doubao'] = {
            'api_key': 'your_doubao_api_key_here',
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model_id': 'ep-20241220102345-xxxxx',
            'max_tokens': '2000',
            'temperature': '0.7'
        }
        
        self.config['analysis'] = {
            'max_keywords': '10',
            'max_summary_length': '200',
            'enable_cache': 'true',
            'cache_duration': '3600'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
        
        print(f"已创建默认配置文件: {self.config_file}")
        print("请编辑配置文件并填入您的豆包API密钥")
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self.config.get('doubao', 'api_key', fallback='')
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.config.get('doubao', 'base_url', fallback='https://ark.cn-beijing.volces.com/api/v3')
    
    def get_model_id(self) -> str:
        """获取模型ID"""
        return self.config.get('doubao', 'model_id', fallback='ep-20241220102345-xxxxx')


def main():
    """主函数 - 示例用法"""
    # 创建配置管理器
    config_manager = DoubaoTextAnalyzerConfig()
    
    # 获取配置
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return
    
    # 创建分析器
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    # 示例文字
    sample_text = """
    人工智能技术正在快速发展，深度学习、机器学习、自然语言处理等技术不断突破。
    这些技术被广泛应用于医疗、金融、教育、交通等各个领域，为人类生活带来了巨大改变。
    然而，AI技术的发展也带来了一些挑战，如数据隐私、算法偏见、就业影响等问题需要认真对待。
    未来，我们需要在推动AI技术发展的同时，确保其安全、可控、有益于人类。
    """
    
    print("🔍 开始分析文字...")
    print(f"文字内容: {sample_text[:100]}...")
    print()
    
    # 提取关键字
    print("📝 提取关键字:")
    keywords = analyzer.extract_keywords(sample_text, max_keywords=8)
    if keywords:
        for i, kw in enumerate(keywords, 1):
            print(f"  {i}. {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f}, 类型: {kw.get('type', 'N/A')})")
    print()
    
    # 情感分析
    print("😊 情感分析:")
    sentiment = analyzer.analyze_sentiment(sample_text)
    if sentiment and 'error' not in sentiment:
        print(f"  情感倾向: {sentiment.get('sentiment', 'N/A')}")
        print(f"  情感强度: {sentiment.get('score', 0):.2f}")
        print(f"  置信度: {sentiment.get('confidence', 0):.2f}")
    print()
    
    # 生成摘要
    print("📄 文字摘要:")
    summary = analyzer.generate_summary(sample_text, max_length=150)
    if summary:
        print(f"  {summary}")
    print()
    
    # 实体识别
    print("🏷️ 实体识别:")
    entities = analyzer.extract_entities(sample_text)
    if entities:
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"  {entity_type}: {', '.join(entity_list)}")


if __name__ == "__main__":
    main()