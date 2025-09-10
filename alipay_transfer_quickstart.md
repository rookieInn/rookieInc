# 支付宝转账接口快速开始指南

## 🚀 5分钟快速接入

### 第一步：准备工作
1. **企业支付宝账户**：确保已开通收款功能
2. **开放平台账号**：注册并登录 [支付宝开放平台](https://open.alipay.com/)

### 第二步：创建应用
1. 进入"开发者中心" → "我的应用"
2. 点击"创建应用"，填写基本信息
3. 记录生成的 **APPID**

### 第三步：添加转账功能
1. 在应用详情页面，点击"功能信息"
2. 添加"单笔转账到支付宝账户"功能
3. 等待审核通过（通常1-3个工作日）

### 第四步：配置密钥
1. 生成RSA密钥对（使用OpenSSL或在线工具）
2. 在"开发设置"中配置应用公钥
3. 记录支付宝公钥

### 第五步：集成代码
选择您使用的编程语言，复制对应的代码示例：

#### Java
```java
// 1. 添加Maven依赖
<dependency>
    <groupId>com.alipay.sdk</groupId>
    <artifactId>alipay-sdk-java</artifactId>
    <version>4.38.10.ALL</version>
</dependency>

// 2. 配置参数
private static final String APP_ID = "your_app_id";
private static final String PRIVATE_KEY = "your_private_key";
private static final String ALIPAY_PUBLIC_KEY = "your_alipay_public_key";

// 3. 调用转账接口
AlipayFundTransToaccountTransferResponse response = simpleTransfer(
    "user@example.com", // 收款方账号
    "1.00",             // 转账金额
    "测试转账"          // 转账备注
);
```

#### Python
```python
# 1. 安装SDK
pip install alipay-sdk-python

# 2. 配置参数
from alipay_transfer_python_example import AlipayTransferExample

transfer = AlipayTransferExample(
    app_id="your_app_id",
    private_key="your_private_key",
    alipay_public_key="your_alipay_public_key"
)

# 3. 调用转账接口
result = transfer.simple_transfer(
    payee_account="user@example.com",
    amount="1.00",
    remark="测试转账"
)
```

#### Node.js
```javascript
// 1. 安装SDK
npm install alipay-sdk

// 2. 配置参数
const AlipayTransferExample = require('./alipay_transfer_nodejs_example');

const transfer = new AlipayTransferExample({
    appId: 'your_app_id',
    privateKey: 'your_private_key',
    alipayPublicKey: 'your_alipay_public_key'
});

// 3. 调用转账接口
const result = await transfer.simpleTransfer(
    'user@example.com', // 收款方账号
    '1.00',             // 转账金额
    '测试转账'          // 转账备注
);
```

## 📋 重要参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| out_biz_no | 商户转账唯一订单号 | TRANSFER_20241201123456 |
| payee_account | 收款方支付宝账号 | user@example.com |
| payee_type | 收款方账户类型 | ALIPAY_LOGONID |
| amount | 转账金额（元） | 1.00 |
| remark | 转账备注 | 测试转账 |

## ⚠️ 重要限制

- **单笔限额**：个人账户最高5万元，企业账户最高10万元
- **日累计限额**：100万元
- **最低金额**：0.1元
- **实名要求**：企业账户必须完成实名认证

## 🧪 测试环境

使用沙箱环境进行测试：
- **网关地址**：`https://openapi.alipaydev.com/gateway.do`
- **测试账号**：在开放平台获取沙箱测试账号
- **测试金额**：建议使用0.01元进行测试

## 🔧 常见问题

### Q1: 提示"应用未开通此功能"
**解决方案**：检查应用是否已添加转账功能，确保状态为"已生效"

### Q2: 提示"签名验证失败"
**解决方案**：检查私钥和公钥是否匹配，确认使用RSA2算法

### Q3: 转账失败，提示"账户不存在"
**解决方案**：检查收款方账户格式是否正确

## 📞 获取帮助

- **官方文档**：https://docs.open.alipay.com/309
- **开放平台**：https://open.alipay.com/
- **技术支持**：通过开放平台在线客服

## 🎯 下一步

1. 完成基础接入后，建议阅读完整的 [接入指南](alipay_transfer_guide.md)
2. 查看详细的 [配置说明](alipay_transfer_config.md)
3. 根据您的技术栈选择合适的 [代码示例](alipay_transfer_java_example.java)

---

**注意**：请确保在正式上线前完成充分的测试，并遵守相关法律法规。