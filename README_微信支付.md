# 微信支付集成方案

## 概述

本项目提供了完整的微信支付集成解决方案，支持小程序支付、H5支付、订单查询、退款等功能。包含后端API服务、前端示例代码和详细的使用文档。

## 功能特性

- ✅ 小程序支付（JSAPI）
- ✅ H5支付（MWEB）
- ✅ 订单查询和状态管理
- ✅ 订单关闭
- ✅ 退款申请
- ✅ 支付回调处理
- ✅ 退款回调处理
- ✅ 支付数据统计
- ✅ 数据库记录管理
- ✅ 签名验证
- ✅ 沙箱环境支持

## 项目结构

```
/workspace/
├── wechat_pay_config.ini      # 微信支付配置文件
├── wechat_pay_core.py         # 微信支付核心模块
├── wechat_pay_api.py          # RESTful API接口
├── wechat_pay_example.py      # Python使用示例
├── miniprogram_pay_example.js # 小程序支付示例
├── wechat_pay.db             # SQLite数据库（自动创建）
└── README_微信支付.md         # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask requests
```

### 2. 配置微信支付

编辑 `wechat_pay_config.ini` 文件，填入你的微信支付配置：

```ini
[WECHAT_PAY]
merchant_id = your_merchant_id_here          # 微信支付商户号
app_id = your_miniprogram_appid_here         # 小程序AppID
api_key = your_wechat_pay_api_key_here       # 微信支付API密钥
cert_path = cert/apiclient_cert.pem          # 证书路径
key_path = cert/apiclient_key.pem            # 私钥路径
notify_url = https://yourdomain.com/api/wechat/pay/notify  # 支付回调URL
```

### 3. 准备证书文件

将微信支付证书文件放在 `cert/` 目录下：
- `apiclient_cert.pem` - 商户证书
- `apiclient_key.pem` - 商户私钥

### 4. 启动API服务

```bash
python wechat_pay_api.py
```

服务将在 `http://localhost:5000` 启动。

### 5. 测试API

访问 `http://localhost:5000` 查看API文档，或运行示例：

```bash
python wechat_pay_example.py
```

## API接口文档

### 基础URL
```
http://localhost:5000
```

### 1. 创建小程序支付订单

**POST** `/api/wechat/pay/miniprogram`

**请求参数：**
```json
{
  "openid": "用户openid",
  "total_fee": 100,
  "body": "商品描述",
  "attach": "附加数据（可选）",
  "out_trade_no": "商户订单号（可选）"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "out_trade_no": "WX20231201123456789",
    "prepay_id": "wx1234567890",
    "miniprogram_params": {
      "appId": "wx1234567890",
      "timeStamp": "1701234567",
      "nonceStr": "abc123",
      "package": "prepay_id=wx1234567890",
      "signType": "MD5",
      "paySign": "SIGNATURE"
    }
  }
}
```

### 2. 创建H5支付订单

**POST** `/api/wechat/pay/h5`

**请求参数：**
```json
{
  "total_fee": 100,
  "body": "商品描述",
  "attach": "附加数据（可选）",
  "out_trade_no": "商户订单号（可选）"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "out_trade_no": "H520231201123456789",
    "prepay_id": "wx1234567890",
    "mweb_url": "https://wx.tenpay.com/cgi-bin/mwebpay/..."
  }
}
```

### 3. 查询支付订单

**POST** `/api/wechat/pay/query`

**请求参数：**
```json
{
  "out_trade_no": "商户订单号"
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "out_trade_no": "WX20231201123456789",
    "trade_state": "SUCCESS",
    "trade_state_desc": "支付成功",
    "transaction_id": "wx1234567890"
  }
}
```

### 4. 申请退款

**POST** `/api/wechat/pay/refund`

**请求参数：**
```json
{
  "out_trade_no": "原订单号",
  "out_refund_no": "退款单号",
  "total_fee": 100,
  "refund_fee": 100,
  "refund_desc": "退款原因（可选）"
}
```

### 5. 获取支付状态

**GET** `/api/wechat/pay/status/{out_trade_no}`

### 6. 获取支付记录

**GET** `/api/wechat/pay/records?page=1&limit=10`

### 7. 获取支付看板

**GET** `/api/wechat/pay/dashboard`

## 小程序集成

### 1. 在小程序中使用

将 `miniprogram_pay_example.js` 中的代码集成到你的小程序项目中。

### 2. 基本使用流程

```javascript
// 1. 创建支付订单
const paymentData = await createMiniprogramPayment({
  openid: '用户openid',
  total_fee: 100,
  body: '商品描述'
});

// 2. 调用微信支付
const payResult = await requestPayment(paymentData.miniprogram_params);

// 3. 查询支付状态
const status = await queryPaymentStatus(paymentData.out_trade_no);
```

### 3. 页面集成示例

```javascript
Page({
  data: {
    orderInfo: {
      openid: '',
      total_fee: 100,
      body: '测试商品'
    }
  },
  
  onPayButtonClick: function() {
    processPayment(this.data.orderInfo).then(result => {
      if (result.success) {
        wx.showToast({
          title: '支付成功',
          icon: 'success'
        });
      }
    });
  }
});
```

## 支付回调处理

### 1. 支付成功回调

微信支付成功后，会调用你配置的 `notify_url`：

```
POST /api/wechat/pay/notify
```

系统会自动：
- 验证签名
- 更新订单状态
- 记录支付结果

### 2. 退款回调

退款处理完成后，会调用退款回调URL：

```
POST /api/wechat/pay/refund/notify
```

## 数据库结构

### payments 表（支付记录）
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    out_trade_no TEXT UNIQUE NOT NULL,
    openid TEXT,
    total_fee INTEGER NOT NULL,
    body TEXT NOT NULL,
    attach TEXT,
    trade_type TEXT NOT NULL,
    prepay_id TEXT,
    transaction_id TEXT,
    trade_state TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### refunds 表（退款记录）
```sql
CREATE TABLE refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    out_trade_no TEXT NOT NULL,
    out_refund_no TEXT UNIQUE NOT NULL,
    refund_fee INTEGER NOT NULL,
    refund_desc TEXT,
    refund_id TEXT,
    refund_status TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 配置说明

### 微信支付配置

| 配置项 | 说明 | 必填 |
|--------|------|------|
| merchant_id | 微信支付商户号 | 是 |
| app_id | 小程序AppID | 是 |
| api_key | 微信支付API密钥 | 是 |
| cert_path | 商户证书路径 | 是（退款需要） |
| key_path | 商户私钥路径 | 是（退款需要） |
| notify_url | 支付回调URL | 是 |
| sandbox_mode | 沙箱模式 | 否 |

### 安全配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| sign_type | 签名算法 | MD5 |
| verify_signature | 验证签名 | true |
| allowed_ips | IP白名单 | 127.0.0.1 |

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| NOAUTH | 商户无此接口权限 | 检查商户号配置 |
| NOTENOUGH | 余额不足 | 检查账户余额 |
| ORDERPAID | 商户订单已支付 | 检查订单状态 |
| ORDERCLOSED | 订单已关闭 | 重新创建订单 |
| SYSTEMERROR | 系统错误 | 稍后重试 |

### 调试模式

在配置文件中设置 `debug_mode = true` 可以开启详细日志：

```ini
[WECHAT_PAY_SETTINGS]
debug_mode = true
log_level = DEBUG
```

## 部署说明

### 1. 生产环境部署

1. 修改配置文件中的URL为生产环境地址
2. 确保HTTPS证书配置正确
3. 配置防火墙开放必要端口
4. 设置日志轮转和监控

### 2. Nginx配置示例

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/wechat/pay/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 系统服务配置

创建 systemd 服务文件：

```ini
[Unit]
Description=WeChat Pay API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 wechat_pay_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 安全建议

1. **保护API密钥**：不要将API密钥提交到代码仓库
2. **使用HTTPS**：生产环境必须使用HTTPS
3. **验证签名**：始终验证微信回调的签名
4. **IP白名单**：限制API访问来源
5. **日志监控**：监控异常支付行为
6. **定期更新**：及时更新证书和密钥

## 常见问题

### Q: 支付回调没有收到？
A: 检查notify_url是否可访问，确保使用HTTPS，检查防火墙设置。

### Q: 签名验证失败？
A: 检查API密钥配置，确保参数编码正确，检查签名算法。

### Q: 退款失败？
A: 检查证书文件是否正确，确保退款金额不超过原订单金额。

### Q: 沙箱环境如何使用？
A: 设置 `sandbox_mode = true`，使用沙箱API密钥进行测试。

## 技术支持

如有问题，请检查：
1. 配置文件是否正确
2. 证书文件是否存在
3. 网络连接是否正常
4. 日志文件中的错误信息

## 更新日志

### v1.0.0
- 初始版本发布
- 支持小程序支付和H5支付
- 支持订单查询和退款
- 支持支付回调处理
- 提供完整的API接口和示例代码