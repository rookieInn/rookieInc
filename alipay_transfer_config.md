# 支付宝转账接口配置说明

## 1. 开放平台配置

### 1.1 创建应用
1. 登录 [支付宝开放平台](https://open.alipay.com/)
2. 进入"开发者中心" → "我的应用"
3. 点击"创建应用"
4. 填写应用信息：
   - 应用名称：自定义
   - 应用类型：网页&移动应用
   - 应用描述：简要说明应用用途

### 1.2 获取应用信息
创建应用后，记录以下信息：
- **APPID**：应用唯一标识
- **应用公钥**：用于支付宝验证签名
- **应用私钥**：用于签名请求

### 1.3 添加功能
1. 在应用详情页面，点击"功能信息"
2. 点击"添加功能"
3. 搜索并添加"单笔转账到支付宝账户"功能
4. 等待功能审核通过（通常1-3个工作日）

## 2. 密钥配置

### 2.1 生成RSA密钥对

#### 使用OpenSSL生成（推荐）
```bash
# 生成私钥
openssl genrsa -out app_private_key.pem 2048

# 生成公钥
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem

# 查看私钥内容
cat app_private_key.pem

# 查看公钥内容
cat app_public_key.pem
```

#### 使用在线工具生成
- 访问支付宝提供的密钥生成工具
- 选择RSA2算法
- 生成并下载密钥文件

### 2.2 配置密钥
1. 在开放平台应用详情页面，点击"开发设置"
2. 在"接口加签方式"中选择"公钥"
3. 将生成的**应用公钥**内容粘贴到"应用公钥"文本框
4. 点击"保存设置"
5. 系统会生成**支付宝公钥**，请记录此公钥

## 3. 环境配置

### 3.1 沙箱环境（测试）
- **网关地址**：`https://openapi.alipaydev.com/gateway.do`
- **用途**：开发测试
- **特点**：使用测试账号，不产生真实资金流动

### 3.2 生产环境
- **网关地址**：`https://openapi.alipay.com/gateway.do`
- **用途**：正式上线
- **特点**：使用真实账号，产生真实资金流动

## 4. 代码配置示例

### 4.1 Java配置
```java
// 配置参数
private static final String APP_ID = "2021001234567890";
private static final String PRIVATE_KEY = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...";
private static final String ALIPAY_PUBLIC_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...";
private static final String GATEWAY_URL = "https://openapi.alipay.com/gateway.do";
```

### 4.2 Python配置
```python
# 配置参数
APP_ID = "2021001234567890"
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END RSA PRIVATE KEY-----"""
ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""
```

### 4.3 Node.js配置
```javascript
const config = {
    appId: '2021001234567890',
    privateKey: `-----BEGIN RSA PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END RSA PRIVATE KEY-----`,
    alipayPublicKey: `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----`
};
```

## 5. 安全配置

### 5.1 密钥安全
- **私钥保护**：私钥必须妥善保管，不能泄露
- **密钥轮换**：定期更换密钥对
- **访问控制**：限制私钥的访问权限

### 5.2 网络安全
- **HTTPS传输**：所有接口调用必须使用HTTPS
- **IP白名单**：在开放平台配置服务器IP白名单
- **请求签名**：所有请求必须进行签名验证

### 5.3 数据安全
- **参数校验**：严格校验所有输入参数
- **金额验证**：确保转账金额在合理范围内
- **订单号唯一性**：确保out_biz_no的唯一性

## 6. 测试配置

### 6.1 沙箱测试账号
1. 在开放平台"沙箱环境"页面获取测试账号
2. 使用测试账号进行转账测试
3. 验证接口调用是否正常

### 6.2 测试用例
```javascript
// 测试用例示例
const testCases = [
    {
        name: "正常转账",
        payeeAccount: "test@example.com",
        amount: "0.01",
        remark: "测试转账"
    },
    {
        name: "大额转账",
        payeeAccount: "test@example.com",
        amount: "100.00",
        remark: "大额测试"
    },
    {
        name: "最小金额转账",
        payeeAccount: "test@example.com",
        amount: "0.10",
        remark: "最小金额测试"
    }
];
```

## 7. 监控配置

### 7.1 日志记录
- 记录所有转账请求和响应
- 记录错误信息和异常情况
- 定期分析日志数据

### 7.2 监控指标
- 转账成功率
- 接口响应时间
- 错误率统计
- 资金流水监控

## 8. 常见问题

### 8.1 配置问题
**Q: 提示"应用未开通此功能"**
A: 检查应用是否已添加"单笔转账到支付宝账户"功能，且状态为"已生效"

**Q: 提示"签名验证失败"**
A: 检查私钥和公钥是否匹配，确认签名算法为RSA2

**Q: 提示"应用ID不存在"**
A: 检查APPID是否正确，确认应用状态正常

### 8.2 接口问题
**Q: 转账失败，提示"账户不存在"**
A: 检查收款方账户是否正确，确认账户类型匹配

**Q: 转账失败，提示"余额不足"**
A: 检查付款方账户余额是否充足

**Q: 转账失败，提示"超出限额"**
A: 检查转账金额是否超出单笔或日累计限额

## 9. 上线检查清单

- [ ] 应用已通过审核
- [ ] 转账功能已开通并生效
- [ ] 密钥配置正确
- [ ] 代码已切换到生产环境
- [ ] 安全配置已完善
- [ ] 监控系统已部署
- [ ] 测试用例已通过
- [ ] 文档已更新

## 10. 联系支持

如遇到技术问题，可通过以下方式获取支持：
- 支付宝开放平台：在线客服
- 技术文档：https://docs.open.alipay.com/
- 开发者社区：https://developer.alipay.com/