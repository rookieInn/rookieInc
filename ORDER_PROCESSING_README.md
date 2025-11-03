# 电商订单数据清洗与异常检测管道

本工具用于处理电商平台每天产生的 10 万条（及以上）订单数据，通过自动化流程实现数据清洗、异常订单识别，并输出结构化结果文件。

## 功能概览

- **数据清洗**：
  - 归一化手机号（E.164 格式），识别并标记无法修复的号码
  - 地址字符清洗、统一空白字符与标点
  - 基于历史订单匹配补全缺失的物流单号，并记录来源与置信度
- **异常检测**：
  - 高频小额下单与短时间内的“爆发式”小额订单
  - 同一 IP 关联多账户 / 大量下单
  - 手机号归属地与收货地址区域不一致
  - Isolation Forest 模型自动识别其它异常订单（可开关）
- **报告输出**：
  - 清洗后的订单数据 (`cleaned_orders.csv`)
  - 异常订单报告 (`anomaly_report.csv`)，包含异常类型、置信度、建议处理方式
  - 可选：处理摘要 JSON（异常分布、清洗统计、物流单号补全数量）

## 快速开始

```bash
pip install -r requirements.txt

python process_orders.py \
  --raw data/orders_20251102.csv \
  --historical data/orders_history.csv \
  --clean-output outputs/cleaned_orders.csv \
  --anomaly-output outputs/anomaly_report.csv \
  --summary
```

常用参数：

- `--config`：加载自定义 JSON 配置（阈值、列名映射等）
- `--disable-ml`：关闭 Isolation Forest 模型，仅使用规则检测
- `--summary-path summary.json`：将处理摘要以 JSON 形式保存

## 数据要求

- 必需字段（可通过配置重命名）：`order_id`, `customer_id`, `order_datetime`, `order_amount`, `phone_number`, `shipping_address`, `ip_address`, `tracking_number`, `carrier`
- 历史订单用于补全物流单号，建议包含与当日订单相同的关键字段

## 配置说明

默认配置位于 `order_processing/config.py`。创建 JSON 配置示例：

```json
{
  "columns": {
    "order_amount": "amount",
    "order_datetime": "created_at"
  },
  "cleaning": {
    "phone_default_region": "CN",
    "min_address_length": 6
  },
  "anomaly": {
    "rules": {
      "small_order_amount": 30,
      "high_frequency_orders_per_day": 10
    },
    "isolation_forest": {
      "enabled": true,
      "contamination": 0.02
    }
  }
}
```

## 输出文件结构

- `cleaned_orders.csv`
  - 原始字段（已清洗）
  - `_raw` 后缀的原始手机号 / 地址
  - `phone_number_validation_status`、`tracking_number_imputed`、`tracking_number_imputation_source` 等辅助字段
- `anomaly_report.csv`
  - `order_id`, `anomaly_type`, `confidence`, `score`, `details`, `suggestion`
- `summary.json`（可选）
  - `cleaning_stats`, `anomaly_total`, `anomaly_breakdown`, `tracking_imputations`

## 处理能力与扩展

- 默认支持单次处理 10 万+ 条记录（Pandas + 向量化操作）
- 如需处理更大规模数据，可通过 `PipelineConfig.chunk_size` 扩展为分批处理
- 支持替换 / 扩展规则与模型，可在 `order_processing/anomaly_detection.py` 中添加自定义逻辑

## 运行测试（即将提供）

项目包含基础单元测试样例（见 `tests/test_order_processing.py`）。执行：

```bash
pytest tests/test_order_processing.py
```

若需集成到现有流水线，可将 `OrderProcessingPipeline` 嵌入 ETL 作业或调度系统中运行。

