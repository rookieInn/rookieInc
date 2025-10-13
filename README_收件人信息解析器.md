# 收件人信息自动识别解析器

## 概述

收件人信息自动识别解析器是一个专门用于解析和识别收件人信息中不同组件的Python工具。它能够自动从文本中提取姓名、手机号码、地址、邮政编码等关键信息，并按照结构化的方式组织数据。

## 功能特性

- ✅ **姓名识别**: 自动识别中文姓名（2-4个字符）
- ✅ **手机号码提取**: 支持中国手机号码格式识别和验证
- ✅ **地址解析**: 智能解析省份、城市、区县和详细地址
- ✅ **邮政编码识别**: 自动提取和验证6位邮政编码
- ✅ **批量处理**: 支持批量解析多个收件人信息
- ✅ **数据验证**: 内置手机号码和邮政编码格式验证
- ✅ **JSON输出**: 支持结构化数据输出
- ✅ **错误处理**: 优雅处理各种边界情况和异常输入

## 安装要求

- Python 3.6+
- 无需额外依赖包（仅使用标准库）

## 快速开始

### 基本使用

```python
from recipient_parser import RecipientParser

# 创建解析器实例
parser = RecipientParser()

# 解析收件人信息
text = "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
result = parser.parse(text)

# 查看解析结果
print(f"姓名: {result.name}")
print(f"手机: {result.phone}")
print(f"地址: {result.address}")
print(f"邮编: {result.postal_code}")
```

### 批量处理

```python
# 批量解析多个收件人信息
texts = [
    "张三 13812345678 北京市朝阳区",
    "李四 上海市浦东新区",
    "王五 广东省深圳市"
]

results = parser.parse_multiple(texts)
for result in results:
    print(f"姓名: {result.name}, 地址: {result.address}")
```

## 数据结构

### RecipientInfo 类

解析结果使用 `RecipientInfo` 数据类存储，包含以下字段：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `name` | str | 收件人姓名 |
| `phone` | str | 手机号码 |
| `address` | str | 完整地址 |
| `postal_code` | str | 邮政编码 |
| `province` | str | 省份/直辖市 |
| `city` | str | 城市 |
| `district` | str | 区县 |
| `detailed_address` | str | 详细地址 |
| `raw_text` | str | 原始输入文本 |

### 方法

- `to_dict()`: 转换为字典格式
- `to_json()`: 转换为JSON字符串

## 使用示例

### 1. 基本解析

```python
from recipient_parser import RecipientParser

parser = RecipientParser()
text = "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
result = parser.parse(text)

print(result.to_json())
```

输出：
```json
{
  "name": "张三",
  "phone": "13812345678",
  "address": "北京 朝阳区 建国门外大街1号",
  "postal_code": "100000",
  "province": "北京",
  "city": null,
  "district": "朝阳区",
  "detailed_address": "建国门外大街1号",
  "raw_text": "张三 13812345678 北京市朝阳区建国门外大街1号 100000"
}
```

### 2. 验证功能

```python
# 验证手机号码
is_valid_phone = parser.validate_phone("13812345678")  # True

# 验证邮政编码
is_valid_postal = parser.validate_postal_code("100000")  # True
```

### 3. 复杂格式处理

```python
# 处理复杂格式的收件人信息
complex_text = "收件人：张三，电话：138-1234-5678，地址：北京市朝阳区建国门外大街1号国贸大厦A座1001室，邮编：100000"
result = parser.parse(complex_text)
```

## 支持的格式

### 手机号码格式
- `13812345678`
- `138-1234-5678`
- `138 1234 5678`
- `+86 138 1234 5678`
- `+86-138-1234-5678`

### 地址格式
- 支持中国所有省份、直辖市、自治区
- 支持市、县、区、镇、乡、村等行政区划
- 支持街道、路、街、巷、弄、号等地址元素

### 邮政编码格式
- 6位数字格式（如：100000）

## 高级用法

### 自定义解析器

```python
from recipient_parser import RecipientParser
import re

class CustomRecipientParser(RecipientParser):
    def extract_name(self, text: str) -> Optional[str]:
        # 自定义姓名提取逻辑
        # 支持带称谓的姓名
        title_pattern = re.compile(r'(先生|女士|小姐|老师|经理|主任|总|博士|教授)\s*([\u4e00-\u9fff]{2,4})')
        match = title_pattern.search(text)
        if match:
            return match.group(2)
        return super().extract_name(text)

# 使用自定义解析器
custom_parser = CustomRecipientParser()
```

### 错误处理

```python
# 处理空输入或无效输入
empty_result = parser.parse("")
print(empty_result.name)  # None

# 处理部分信息缺失
partial_result = parser.parse("张三 北京市朝阳区")
print(partial_result.name)  # 张三
print(partial_result.phone)  # None
```

## 性能特性

- **高效解析**: 使用正则表达式优化，支持大量数据快速处理
- **内存友好**: 无需额外依赖，内存占用小
- **批量处理**: 支持批量解析，提高处理效率

## 测试

运行测试套件：

```bash
python test_recipient_parser.py
```

运行示例：

```bash
python recipient_parser_example.py
```

## 限制和注意事项

1. **姓名识别**: 目前主要支持2-4个中文字符的姓名
2. **地址解析**: 主要针对中国大陆地址格式优化
3. **手机号码**: 仅支持中国大陆手机号码格式
4. **邮政编码**: 仅支持6位数字格式的中国邮政编码

## 扩展建议

1. **多语言支持**: 可以扩展支持英文姓名和地址
2. **更多国家**: 可以添加其他国家/地区的地址格式支持
3. **机器学习**: 可以集成机器学习模型提高识别准确率
4. **API接口**: 可以封装为REST API服务

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的收件人信息解析
- 包含姓名、手机号、地址、邮编识别
- 提供批量处理和验证功能