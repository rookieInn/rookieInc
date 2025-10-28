# 豆包文字分析器

一个基于豆包API的文字分析和关键字提取工具，支持关键字提取、情感分析、摘要生成、实体识别等功能。

## 功能特性

- ✅ **关键字提取**: 智能提取文字中的关键信息，支持权重评分和类型标注
- ✅ **情感分析**: 分析文字的情感倾向和强度
- ✅ **摘要生成**: 自动生成文字摘要，支持自定义长度
- ✅ **实体识别**: 识别人名、地名、机构名、时间、数字等实体
- ✅ **批量处理**: 支持批量分析多篇文字
- ✅ **配置管理**: 灵活的配置文件管理
- ✅ **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
pip install requests configparser
```

## 快速开始

### 1. 配置API密钥

编辑 `doubao_config.ini` 文件，填入您的豆包API密钥：

```ini
[doubao]
api_key = your_actual_api_key_here
base_url = https://ark.cn-beijing.volces.com/api/v3
model_id = ep-20241220102345-xxxxx
```

### 2. 基础使用

```python
from doubao_text_analyzer import DoubaoTextAnalyzer, DoubaoTextAnalyzerConfig

# 创建配置管理器
config_manager = DoubaoTextAnalyzerConfig()

# 创建分析器
analyzer = DoubaoTextAnalyzer(
    api_key=config_manager.get_api_key(),
    base_url=config_manager.get_base_url()
)

# 要分析的文字
text = "人工智能技术正在快速发展，深度学习、机器学习等技术不断突破。"

# 提取关键字
keywords = analyzer.extract_keywords(text, max_keywords=5)
print("关键字:", [kw['word'] for kw in keywords])

# 情感分析
sentiment = analyzer.analyze_sentiment(text)
print("情感倾向:", sentiment['sentiment'])

# 生成摘要
summary = analyzer.generate_summary(text, max_length=100)
print("摘要:", summary)
```

### 3. 运行示例

```bash
# 运行基础示例
python example_doubao_usage.py

# 运行测试
python test_doubao_analyzer.py

# 运行主程序
python doubao_text_analyzer.py
```

## 详细使用说明

### 关键字提取

```python
# 提取关键字，支持权重和类型
keywords = analyzer.extract_keywords(text, max_keywords=10)

for kw in keywords:
    print(f"词: {kw['word']}")
    print(f"权重: {kw['weight']}")
    print(f"类型: {kw['type']}")
    print(f"描述: {kw['description']}")
```

### 情感分析

```python
# 情感分析
sentiment = analyzer.analyze_sentiment(text)

print(f"情感倾向: {sentiment['sentiment']}")  # 积极/消极/中性
print(f"情感强度: {sentiment['score']}")      # 0-1
print(f"置信度: {sentiment['confidence']}")   # 0-1
print(f"主要因素: {sentiment['factors']}")    # 影响因素列表
```

### 摘要生成

```python
# 生成摘要
summary = analyzer.generate_summary(text, max_length=200)
print(f"摘要: {summary}")
```

### 实体识别

```python
# 实体识别
entities = analyzer.extract_entities(text)

for entity_type, entity_list in entities.items():
    if entity_list:
        print(f"{entity_type}: {', '.join(entity_list)}")
```

### 批量分析

```python
# 批量分析多篇文字
texts = [
    "第一篇文字内容...",
    "第二篇文字内容...",
    "第三篇文字内容..."
]

results = []
for text in texts:
    keywords = analyzer.extract_keywords(text)
    sentiment = analyzer.analyze_sentiment(text)
    summary = analyzer.generate_summary(text)
    
    results.append({
        'keywords': [kw['word'] for kw in keywords],
        'sentiment': sentiment['sentiment'],
        'summary': summary
    })
```

## 配置说明

### doubao_config.ini 配置文件

```ini
[doubao]
# 豆包API配置
api_key = your_doubao_api_key_here
base_url = https://ark.cn-beijing.volces.com/api/v3
model_id = ep-20241220102345-xxxxx
max_tokens = 2000
temperature = 0.7

[analysis]
# 分析参数配置
max_keywords = 10
max_summary_length = 200
enable_cache = true
cache_duration = 3600

[logging]
# 日志配置
level = INFO
log_file = doubao_analyzer.log
max_file_size = 10MB
backup_count = 5
```

### 配置参数说明

- `api_key`: 豆包API密钥（必填）
- `base_url`: API基础URL
- `model_id`: 使用的模型ID
- `max_tokens`: 最大token数
- `temperature`: 生成温度（0-1）
- `max_keywords`: 默认最大关键字数量
- `max_summary_length`: 默认摘要最大长度

## API接口说明

### DoubaoTextAnalyzer 类

#### 初始化
```python
analyzer = DoubaoTextAnalyzer(api_key, base_url=None)
```

#### 主要方法

1. **extract_keywords(text, max_keywords=10)**
   - 提取关键字
   - 返回关键字列表，包含词、权重、类型、描述

2. **analyze_sentiment(text)**
   - 情感分析
   - 返回情感倾向、强度、置信度、影响因素

3. **generate_summary(text, max_length=200)**
   - 生成摘要
   - 返回文字摘要

4. **extract_entities(text)**
   - 实体识别
   - 返回按类型分组的实体列表

5. **analyze_text(text, analysis_type)**
   - 通用分析接口
   - 支持多种分析类型

## 错误处理

工具包含完善的错误处理机制：

- API调用失败时返回None或空结果
- 详细的错误日志记录
- 网络超时处理
- 配置验证

## 日志记录

- 日志文件：`doubao_analyzer.log`
- 日志级别：INFO
- 包含API调用、错误信息、分析结果等

## 注意事项

1. **API密钥**: 请确保使用有效的豆包API密钥
2. **网络连接**: 需要稳定的网络连接访问豆包API
3. **文字长度**: 建议单次分析的文字长度不超过2000字符
4. **调用频率**: 注意API调用频率限制
5. **模型ID**: 确保使用正确的模型ID

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查 `doubao_config.ini` 中的API密钥是否正确
   - 确认API密钥是否有效且有足够额度

2. **网络连接失败**
   - 检查网络连接
   - 确认API地址是否正确

3. **分析结果为空**
   - 检查输入文字是否为空
   - 查看日志文件了解详细错误信息

4. **模型ID错误**
   - 确认使用的模型ID是否正确
   - 检查模型是否可用

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 示例输出

### 关键字提取示例
```
关键字:
  1. 人工智能 (权重: 0.95, 类型: 名词)
  2. 技术 (权重: 0.88, 类型: 名词)
  3. 发展 (权重: 0.82, 类型: 动词)
  4. 深度学习 (权重: 0.78, 类型: 名词)
  5. 机器学习 (权重: 0.75, 类型: 名词)
```

### 情感分析示例
```
情感倾向: 积极
情感强度: 0.85
置信度: 0.92
主要因素: ['技术发展', '应用广泛', '改变生活']
```

### 实体识别示例
```
person: ['李教授', '张三']
location: ['北京', '上海']
organization: ['清华大学', 'OpenAI', 'Google']
time: ['2024年12月', '2030年']
number: ['1500亿美元', '30%']
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持关键字提取、情感分析、摘要生成、实体识别
- 支持批量处理和配置管理
- 完善的错误处理和日志记录