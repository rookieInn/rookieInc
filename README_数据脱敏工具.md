# 数据脱敏工具

一个用于前端页面中手机号和身份证号脱敏的完整解决方案。

## 功能特性

### 🔐 核心功能
- **手机号脱敏**：支持各种格式的手机号脱敏处理
- **身份证号脱敏**：支持18位和15位身份证号脱敏
- **批量处理**：支持批量数据脱敏处理
- **格式识别**：自动识别数据类型和格式
- **实时预览**：即时显示脱敏效果

### 📱 支持的手机号格式
- 标准格式：`13812345678` → `138****5678`
- 国际格式：`+86-138-1234-5678` → `+86-138-****-5678`
- 带分隔符：`138-1234-5678` → `138-****-5678`

### 🆔 支持的身份证号格式
- 18位身份证：`110101199001011234` → `11010119900101****`
- 15位身份证：`110101900101123` → `11010190010****`
- 带校验位：`11010119900101123X` → `11010119900101****`

## 文件结构

```
/workspace/
├── desensitization.html          # 主页面文件
├── desensitization-utils.js      # 脱敏工具库
└── README_数据脱敏工具.md        # 使用说明
```

## 使用方法

### 1. 直接使用HTML页面

打开 `desensitization.html` 文件即可使用完整的脱敏工具界面。

### 2. 集成到现有项目

#### 引入工具库
```html
<script src="desensitization-utils.js"></script>
```

#### 基本使用
```javascript
// 单个数据脱敏
const result = desensitizeData('13812345678');
console.log(result);
// 输出: { original: '13812345678', desensitized: '138****5678', type: 'phone' }

// 手机号脱敏
const phone = desensitizePhone('13812345678');
console.log(phone); // 输出: 138****5678

// 身份证号脱敏
const idCard = desensitizeIdCard('110101199001011234');
console.log(idCard); // 输出: 11010119900101****

// 批量脱敏
const dataList = ['13812345678', '110101199001011234', '15987654321'];
const results = batchDesensitize(dataList);
console.log(results);
```

#### 高级功能
```javascript
// 自定义脱敏规则
const custom = customDesensitize('13812345678', {
    keepStart: 3,    // 保留前3位
    keepEnd: 4,      // 保留后4位
    maskChar: '*',   // 使用*号脱敏
    maskLength: 4    // 脱敏4位
});

// 高级脱敏（包含格式检测）
const advanced = advancedDesensitize('+86-138-1234-5678');
console.log(advanced);
// 输出: { original: '+86-138-1234-5678', desensitized: '+86-138-****-5678', type: 'phone', format: 'international' }

// 数据验证
const isValidPhone = isValidPhone('13812345678'); // true
const isValidId = isValidIdCard('110101199001011234'); // true
```

## API 参考

### DesensitizationUtils 类

#### 方法列表

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `desensitizeData(data)` | `string` | `object\|null` | 通用脱敏方法 |
| `desensitizePhone(phone)` | `string` | `string` | 手机号脱敏 |
| `desensitizeIdCard(idCard)` | `string` | `string` | 身份证号脱敏 |
| `batchDesensitize(dataList)` | `Array<string>` | `Array<object>` | 批量脱敏 |
| `isValidPhone(phone)` | `string` | `boolean` | 验证手机号格式 |
| `isValidIdCard(idCard)` | `string` | `boolean` | 验证身份证号格式 |
| `customDesensitize(data, options)` | `string, object` | `string` | 自定义脱敏规则 |
| `advancedDesensitize(data)` | `string` | `object\|null` | 高级脱敏处理 |

#### 脱敏结果对象结构

```javascript
{
    original: string,      // 原始数据
    desensitized: string,  // 脱敏后数据
    type: string,          // 数据类型：'phone' 或 'id'
    format?: string        // 格式类型（仅高级脱敏）
}
```

## 脱敏规则

### 手机号脱敏规则
- 保留前3位和后4位
- 中间4位用 `****` 替换
- 支持各种格式的自动识别和处理

### 身份证号脱敏规则
- 18位身份证：保留前14位，后4位用 `****` 替换
- 15位身份证：保留前11位，后4位用 `****` 替换
- 保持原始格式（如带分隔符）

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 安全说明

- 本工具仅在前端进行脱敏处理
- 不会向任何服务器发送敏感数据
- 所有处理都在本地浏览器中完成
- 建议在生产环境中结合后端验证

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持手机号和身份证号脱敏
- 提供完整的Web界面
- 支持批量处理功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

---

**注意**：本工具仅用于数据脱敏展示和测试，在生产环境中使用前请确保符合相关的数据保护法规。