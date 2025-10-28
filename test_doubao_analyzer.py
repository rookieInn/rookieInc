#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包文字分析器测试脚本
"""

import sys
import os
import json
from datetime import datetime
from doubao_text_analyzer import DoubaoTextAnalyzer, DoubaoTextAnalyzerConfig


def test_keyword_extraction():
    """测试关键字提取功能"""
    print("=" * 50)
    print("🔍 测试关键字提取功能")
    print("=" * 50)
    
    # 测试文字
    test_texts = [
        "人工智能技术正在快速发展，深度学习、机器学习、自然语言处理等技术不断突破。这些技术被广泛应用于医疗、金融、教育、交通等各个领域。",
        "今天天气很好，阳光明媚，适合出去散步。我决定去公园走走，呼吸新鲜空气，放松一下心情。",
        "Python是一种高级编程语言，具有简洁的语法和强大的功能。它被广泛用于数据分析、机器学习、Web开发等领域。"
    ]
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return False
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试文字 {i}:")
        print(f"内容: {text[:80]}...")
        
        keywords = analyzer.extract_keywords(text, max_keywords=5)
        if keywords:
            print("关键字:")
            for j, kw in enumerate(keywords, 1):
                print(f"  {j}. {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f})")
        else:
            print("❌ 关键字提取失败")
    
    return True


def test_sentiment_analysis():
    """测试情感分析功能"""
    print("\n" + "=" * 50)
    print("😊 测试情感分析功能")
    print("=" * 50)
    
    test_texts = [
        "今天心情很好，工作顺利，生活充满希望！",
        "这个产品质量太差了，完全不值这个价格，非常失望。",
        "今天是个普通的日子，没有什么特别的事情发生。",
        "虽然遇到了一些困难，但我相信通过努力一定能够克服。"
    ]
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return False
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试文字 {i}:")
        print(f"内容: {text}")
        
        sentiment = analyzer.analyze_sentiment(text)
        if sentiment and 'error' not in sentiment:
            print(f"情感倾向: {sentiment.get('sentiment', 'N/A')}")
            print(f"情感强度: {sentiment.get('score', 0):.2f}")
            print(f"置信度: {sentiment.get('confidence', 0):.2f}")
        else:
            print("❌ 情感分析失败")
    
    return True


def test_summary_generation():
    """测试摘要生成功能"""
    print("\n" + "=" * 50)
    print("📄 测试摘要生成功能")
    print("=" * 50)
    
    long_text = """
    人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、
    图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
    
    人工智能的发展历程可以分为几个阶段：第一阶段是符号主义阶段，主要研究如何用符号来表示知识和推理；
    第二阶段是连接主义阶段，主要研究神经网络和深度学习；第三阶段是统计学习阶段，主要研究机器学习算法；
    第四阶段是深度学习阶段，主要研究深度神经网络和大数据。
    
    目前，人工智能技术已经在很多领域得到了广泛应用，包括医疗诊断、金融风控、自动驾驶、智能推荐、
    语音识别、图像识别等。这些应用不仅提高了工作效率，也改变了人们的生活方式。
    
    然而，人工智能的发展也带来了一些挑战和问题，如数据隐私保护、算法偏见、就业影响、伦理道德等。
    这些问题需要我们在推动AI技术发展的同时，认真对待和解决。
    """
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return False
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    print("📝 原文:")
    print(long_text[:200] + "...")
    
    summary = analyzer.generate_summary(long_text, max_length=150)
    if summary:
        print(f"\n📄 摘要:")
        print(summary)
    else:
        print("❌ 摘要生成失败")
    
    return True


def test_entity_recognition():
    """测试实体识别功能"""
    print("\n" + "=" * 50)
    print("🏷️ 测试实体识别功能")
    print("=" * 50)
    
    test_text = """
    2024年12月，在北京举行的AI技术大会上，来自清华大学、北京大学、中科院等知名机构的专家们
    讨论了人工智能技术的发展趋势。会议期间，OpenAI、Google、百度、阿里巴巴等科技公司
    展示了最新的AI产品和研究成果。预计到2025年，全球AI市场规模将达到5000亿美元。
    """
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return False
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    print("📝 测试文字:")
    print(test_text)
    
    entities = analyzer.extract_entities(test_text)
    if entities:
        print("\n🏷️ 识别到的实体:")
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"  {entity_type}: {', '.join(entity_list)}")
    else:
        print("❌ 实体识别失败")
    
    return True


def test_comprehensive_analysis():
    """综合测试"""
    print("\n" + "=" * 50)
    print("🔬 综合测试")
    print("=" * 50)
    
    sample_text = """
    随着科技的快速发展，人工智能技术正在深刻改变着我们的生活方式。从智能手机的语音助手，
    到自动驾驶汽车，再到医疗诊断系统，AI技术已经渗透到我们生活的方方面面。
    
    在商业领域，企业利用AI技术进行数据分析、客户服务、供应链优化等，大大提高了运营效率。
    在教育领域，AI技术为个性化学习、智能辅导、自动评分等提供了新的可能性。
    
    然而，AI技术的发展也带来了一些挑战。数据隐私保护、算法公平性、就业影响等问题
    需要我们认真思考和解决。未来，我们需要在推动AI技术发展的同时，
    确保其安全、可控、有益于人类社会的发展。
    """
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        return False
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    print("📝 原文:")
    print(sample_text)
    print()
    
    # 关键字提取
    print("🔍 关键字提取:")
    keywords = analyzer.extract_keywords(sample_text, max_keywords=8)
    if keywords:
        for i, kw in enumerate(keywords, 1):
            print(f"  {i}. {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f})")
    print()
    
    # 情感分析
    print("😊 情感分析:")
    sentiment = analyzer.analyze_sentiment(sample_text)
    if sentiment and 'error' not in sentiment:
        print(f"  情感倾向: {sentiment.get('sentiment', 'N/A')}")
        print(f"  情感强度: {sentiment.get('score', 0):.2f}")
    print()
    
    # 摘要生成
    print("📄 摘要:")
    summary = analyzer.generate_summary(sample_text, max_length=200)
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
    
    return True


def main():
    """主测试函数"""
    print("🚀 豆包文字分析器测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查配置文件
    if not os.path.exists('doubao_config.ini'):
        print("❌ 配置文件 doubao_config.ini 不存在")
        print("请先运行 python doubao_text_analyzer.py 创建配置文件")
        return
    
    # 运行各项测试
    tests = [
        ("关键字提取", test_keyword_extraction),
        ("情感分析", test_sentiment_analysis),
        ("摘要生成", test_summary_generation),
        ("实体识别", test_entity_recognition),
        ("综合测试", test_comprehensive_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 开始测试: {test_name}")
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()