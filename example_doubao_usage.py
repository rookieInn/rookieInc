#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包文字分析器使用示例
"""

from doubao_text_analyzer import DoubaoTextAnalyzer, DoubaoTextAnalyzerConfig
import json


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("📚 豆包文字分析器 - 基础使用示例")
    print("=" * 60)
    
    # 1. 创建配置管理器
    config_manager = DoubaoTextAnalyzerConfig()
    
    # 2. 获取配置
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先在 doubao_config.ini 中配置您的豆包API密钥")
        print("配置步骤:")
        print("1. 打开 doubao_config.ini 文件")
        print("2. 将 api_key 替换为您的实际API密钥")
        print("3. 保存文件后重新运行此示例")
        return
    
    # 3. 创建分析器实例
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    # 4. 准备要分析的文字
    text = """
    人工智能技术正在快速发展，深度学习、机器学习、自然语言处理等技术不断突破。
    这些技术被广泛应用于医疗、金融、教育、交通等各个领域，为人类生活带来了巨大改变。
    然而，AI技术的发展也带来了一些挑战，如数据隐私、算法偏见、就业影响等问题需要认真对待。
    未来，我们需要在推动AI技术发展的同时，确保其安全、可控、有益于人类。
    """
    
    print(f"📝 要分析的文字:\n{text}\n")
    
    # 5. 提取关键字
    print("🔍 提取关键字:")
    keywords = analyzer.extract_keywords(text, max_keywords=8)
    if keywords:
        for i, kw in enumerate(keywords, 1):
            print(f"  {i}. {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f}, 类型: {kw.get('type', 'N/A')})")
    else:
        print("  ❌ 关键字提取失败")
    print()
    
    # 6. 情感分析
    print("😊 情感分析:")
    sentiment = analyzer.analyze_sentiment(text)
    if sentiment and 'error' not in sentiment:
        print(f"  情感倾向: {sentiment.get('sentiment', 'N/A')}")
        print(f"  情感强度: {sentiment.get('score', 0):.2f}")
        print(f"  置信度: {sentiment.get('confidence', 0):.2f}")
        if sentiment.get('factors'):
            print(f"  主要因素: {', '.join(sentiment.get('factors', []))}")
    else:
        print("  ❌ 情感分析失败")
    print()
    
    # 7. 生成摘要
    print("📄 文字摘要:")
    summary = analyzer.generate_summary(text, max_length=150)
    if summary:
        print(f"  {summary}")
    else:
        print("  ❌ 摘要生成失败")
    print()
    
    # 8. 实体识别
    print("🏷️ 实体识别:")
    entities = analyzer.extract_entities(text)
    if entities:
        for entity_type, entity_list in entities.items():
            if entity_list:
                print(f"  {entity_type}: {', '.join(entity_list)}")
    else:
        print("  ❌ 实体识别失败")


def example_batch_analysis():
    """批量分析示例"""
    print("\n" + "=" * 60)
    print("📚 豆包文字分析器 - 批量分析示例")
    print("=" * 60)
    
    # 准备多篇文字
    texts = [
        {
            "title": "科技新闻",
            "content": "苹果公司发布了最新的iPhone 15系列手机，搭载了A17 Pro芯片，支持5G网络，摄像头性能大幅提升。"
        },
        {
            "title": "体育新闻", 
            "content": "在昨晚的足球比赛中，巴塞罗那队以3-1的比分战胜了皇家马德里队，梅西表现出色，独中两元。"
        },
        {
            "title": "财经新闻",
            "content": "今日股市表现强劲，上证指数上涨2.5%，深证成指上涨3.1%，科技股领涨，投资者信心明显回升。"
        }
    ]
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先配置API密钥")
        return
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    # 批量分析
    results = []
    for i, article in enumerate(texts, 1):
        print(f"\n📰 文章 {i}: {article['title']}")
        print(f"内容: {article['content']}")
        
        # 提取关键字
        keywords = analyzer.extract_keywords(article['content'], max_keywords=5)
        keyword_list = [kw.get('word', '') for kw in keywords] if keywords else []
        
        # 情感分析
        sentiment = analyzer.analyze_sentiment(article['content'])
        sentiment_label = sentiment.get('sentiment', 'N/A') if sentiment and 'error' not in sentiment else 'N/A'
        
        # 生成摘要
        summary = analyzer.generate_summary(article['content'], max_length=100)
        
        result = {
            'title': article['title'],
            'keywords': keyword_list,
            'sentiment': sentiment_label,
            'summary': summary
        }
        results.append(result)
        
        print(f"关键字: {', '.join(keyword_list)}")
        print(f"情感: {sentiment_label}")
        print(f"摘要: {summary}")
    
    # 保存结果
    with open('batch_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 批量分析结果已保存到 batch_analysis_results.json")


def example_custom_analysis():
    """自定义分析示例"""
    print("\n" + "=" * 60)
    print("📚 豆包文字分析器 - 自定义分析示例")
    print("=" * 60)
    
    config_manager = DoubaoTextAnalyzerConfig()
    api_key = config_manager.get_api_key()
    base_url = config_manager.get_base_url()
    
    if not api_key or api_key == 'your_doubao_api_key_here':
        print("❌ 请先配置API密钥")
        return
    
    analyzer = DoubaoTextAnalyzer(api_key, base_url)
    
    # 自定义分析函数
    def analyze_news_article(text):
        """分析新闻文章"""
        print("📰 新闻文章分析:")
        
        # 提取关键字
        keywords = analyzer.extract_keywords(text, max_keywords=10)
        if keywords:
            print("  🔍 关键字:")
            for kw in keywords:
                print(f"    - {kw.get('word', 'N/A')} (权重: {kw.get('weight', 0):.2f})")
        
        # 情感分析
        sentiment = analyzer.analyze_sentiment(text)
        if sentiment and 'error' not in sentiment:
            print(f"  😊 情感倾向: {sentiment.get('sentiment', 'N/A')}")
            print(f"  📊 情感强度: {sentiment.get('score', 0):.2f}")
        
        # 实体识别
        entities = analyzer.extract_entities(text)
        if entities:
            print("  🏷️ 实体识别:")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    print(f"    {entity_type}: {', '.join(entity_list)}")
        
        # 生成摘要
        summary = analyzer.generate_summary(text, max_length=200)
        if summary:
            print(f"  📄 摘要: {summary}")
    
    # 测试新闻文章
    news_text = """
    2024年12月，在北京举行的全球人工智能大会上，来自世界各地的专家学者齐聚一堂，
    共同探讨AI技术的最新发展趋势。会议期间，OpenAI、Google、百度、阿里巴巴等
    知名科技公司展示了他们最新的AI产品和研究成果。
    
    清华大学计算机系主任李教授在主题演讲中表示，人工智能技术正在从感知智能向认知智能转变，
    未来将更加注重理解、推理和创造能力。他预测，到2030年，AI技术将在医疗、教育、
    交通等领域实现重大突破。
    
    会议还发布了《全球AI发展报告2024》，报告显示，全球AI投资总额达到1500亿美元，
    同比增长25%。其中，中国在AI领域的投资占比达到30%，仅次于美国。
    """
    
    analyze_news_article(news_text)


def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("📚 豆包文字分析器 - 错误处理示例")
    print("=" * 60)
    
    # 使用错误的API密钥测试错误处理
    analyzer = DoubaoTextAnalyzer("invalid_api_key")
    
    text = "这是一个测试文字。"
    
    print("🧪 测试错误处理:")
    print(f"文字: {text}")
    
    # 测试各种分析功能
    functions = [
        ("关键字提取", lambda: analyzer.extract_keywords(text)),
        ("情感分析", lambda: analyzer.analyze_sentiment(text)),
        ("摘要生成", lambda: analyzer.generate_summary(text)),
        ("实体识别", lambda: analyzer.extract_entities(text))
    ]
    
    for func_name, func in functions:
        try:
            result = func()
            if result:
                print(f"  ✅ {func_name}: 成功")
            else:
                print(f"  ❌ {func_name}: 失败")
        except Exception as e:
            print(f"  ⚠️ {func_name}: 异常 - {e}")


def main():
    """主函数"""
    print("🚀 豆包文字分析器使用示例")
    print("=" * 60)
    
    # 运行各种示例
    examples = [
        ("基础使用", example_basic_usage),
        ("批量分析", example_batch_analysis),
        ("自定义分析", example_custom_analysis),
        ("错误处理", example_error_handling)
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n🧪 运行示例: {example_name}")
            example_func()
        except Exception as e:
            print(f"❌ 示例 {example_name} 运行失败: {e}")
    
    print("\n" + "=" * 60)
    print("📖 更多使用方法请参考:")
    print("  - doubao_text_analyzer.py: 主要功能模块")
    print("  - test_doubao_analyzer.py: 测试脚本")
    print("  - doubao_config.ini: 配置文件")
    print("=" * 60)


if __name__ == "__main__":
    main()