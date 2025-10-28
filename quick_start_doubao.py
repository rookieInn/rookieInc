#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包文字分析器快速启动脚本
"""

import os
import sys
from doubao_text_analyzer import DoubaoTextAnalyzer, DoubaoTextAnalyzerConfig


def quick_analyze():
    """快速分析示例文字"""
    print("🚀 豆包文字分析器 - 快速启动")
    print("=" * 50)
    
    # 检查配置
    if not os.path.exists('doubao_config.ini'):
        print("❌ 配置文件不存在，正在创建...")
        config_manager = DoubaoTextAnalyzerConfig()
        print("✅ 配置文件已创建，请编辑 doubao_config.ini 并填入您的API密钥")
        return
    
    # 加载配置
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        print("\n配置步骤:")
        print("1. 打开 doubao_config.ini 文件")
        print("2. 将 api_key = your_doubao_api_key_here 替换为您的实际API密钥")
        print("3. 保存文件后重新运行此脚本")
        return
    
    # 创建分析器
    analyzer = DoubaoTextAnalyzer(api_key, config_manager.get_base_url())
    
    # 示例文字
    sample_texts = [
        "人工智能技术正在快速发展，深度学习、机器学习、自然语言处理等技术不断突破。这些技术被广泛应用于医疗、金融、教育、交通等各个领域，为人类生活带来了巨大改变。",
        "今天天气很好，阳光明媚，适合出去散步。我决定去公园走走，呼吸新鲜空气，放松一下心情。",
        "Python是一种高级编程语言，具有简洁的语法和强大的功能。它被广泛用于数据分析、机器学习、Web开发等领域。"
    ]
    
    print("📝 开始分析示例文字...\n")
    
    for i, text in enumerate(sample_texts, 1):
        print(f"📄 示例 {i}:")
        print(f"内容: {text[:80]}...")
        
        # 提取关键字
        print("🔍 关键字提取:")
        keywords = analyzer.extract_keywords(text, max_keywords=5)
        if keywords:
            for j, kw in enumerate(keywords, 1):
                print(f"  {j}. {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f})")
        else:
            print("  ❌ 提取失败")
        
        # 情感分析
        print("😊 情感分析:")
        sentiment = analyzer.analyze_sentiment(text)
        if sentiment and 'error' not in sentiment:
            print(f"  倾向: {sentiment.get('sentiment', 'N/A')} (强度: {sentiment.get('score', 0):.2f})")
        else:
            print("  ❌ 分析失败")
        
        # 生成摘要
        print("📄 摘要:")
        summary = analyzer.generate_summary(text, max_length=100)
        if summary:
            print(f"  {summary}")
        else:
            print("  ❌ 生成失败")
        
        print("-" * 50)
    
    print("\n✅ 快速分析完成！")
    print("\n📚 更多功能请参考:")
    print("  - python example_doubao_usage.py  # 详细使用示例")
    print("  - python test_doubao_analyzer.py  # 完整测试")
    print("  - README_豆包文字分析.md         # 详细文档")


def interactive_analyze():
    """交互式分析"""
    print("\n🎯 交互式文字分析")
    print("=" * 50)
    
    # 检查配置
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先配置API密钥")
        return
    
    analyzer = DoubaoTextAnalyzer(api_key, config_manager.get_base_url())
    
    print("请输入要分析的文字（输入 'quit' 退出）:")
    
    while True:
        try:
            text = input("\n📝 文字: ").strip()
            
            if text.lower() == 'quit':
                print("👋 再见！")
                break
            
            if not text:
                print("⚠️ 请输入文字内容")
                continue
            
            print("\n🔍 分析中...")
            
            # 提取关键字
            keywords = analyzer.extract_keywords(text, max_keywords=8)
            if keywords:
                print("关键字:", ", ".join([kw.get('word', '') for kw in keywords]))
            
            # 情感分析
            sentiment = analyzer.analyze_sentiment(text)
            if sentiment and 'error' not in sentiment:
                print(f"情感: {sentiment.get('sentiment', 'N/A')} (强度: {sentiment.get('score', 0):.2f})")
            
            # 生成摘要
            summary = analyzer.generate_summary(text, max_length=150)
            if summary:
                print(f"摘要: {summary}")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 分析出错: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_analyze()
    else:
        quick_analyze()


if __name__ == "__main__":
    main()