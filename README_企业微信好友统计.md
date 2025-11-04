# 企业微信好友变更统计工具

该工具基于企业微信「联系客户」数据统计接口，自动记录某个企业账户每日新增好友数量以及被客户主动删除（负反馈）的人数，并将数据持久化到本地 JSON 文件，便于后续分析或可视化。

## 功能亮点

- 🔐 **官方接口**：使用企业微信 `externalcontact/get_user_behavior_data` 接口，数据准确可靠。
- 📅 **按日追踪**：支持指定日期或日期范围的批量采集，默认采集昨天的数据。
- 👥 **多员工支持**：一次性统计多个成员（最多 100 个 / 次），也支持按部门统计。
- 📦 **本地持久化**：数据默认保存到 `data/friend_stats.json`，可自定义路径。
- 📈 **快速汇总**：内置 `summary` 命令，支持展示汇总表或按员工拆分的明细表。

## 快速开始

### 1. 准备配置

复制示例配置文件：

```bash
cp friend_tracker_config.example.json friend_tracker_config.json
```

按需修改以下字段：

- `corp_id`：企业 ID，可在「我的企业」->「企业信息」中查看。
- `corp_secret`：应用或者自建 API 凭证对应的 Secret，需要具备「客户联系」数据统计权限。
- `user_ids`：需要统计的内部成员 `userid` 列表。
- `party_ids`（可选）：需要统计的部门 ID 列表。
- `storage.file_path`：数据输出路径，默认 `data/friend_stats.json`。
- `logging.file`：日志输出文件，可为空表示仅终端输出。

> ⚠️ **提示**：`user_ids` 与 `party_ids` 至少需要配置一个，否则无法调用接口。

### 2. 安装依赖

```bash
pip install requests
```

如果运行环境为 Python 3.8 及以下，还需安装：

```bash
pip install backports.zoneinfo
```

### 3. 采集数据

```bash
# 采集某一天的数据（默认昨天）
python enterprise_friend_tracker.py collect --config friend_tracker_config.json

# 显式指定日期
python enterprise_friend_tracker.py collect --config friend_tracker_config.json --date 2025-11-03

# 批量采集一段时间（包含起止日期）
python enterprise_friend_tracker.py collect --config friend_tracker_config.json --start-date 2025-11-01 --end-date 2025-11-07

# 采集完成后立即展示汇总
python enterprise_friend_tracker.py collect --config friend_tracker_config.json --date 2025-11-03 --print-summary
```

### 4. 查看历史汇总

```bash
# 查看最近 14 天的汇总
python enterprise_friend_tracker.py summary --config friend_tracker_config.json --limit 14

# 查看所有明细，按员工拆分
python enterprise_friend_tracker.py summary --config friend_tracker_config.json --detailed
```

## 输出数据格式

默认输出文件 `data/friend_stats.json` 为一个 JSON 列表，每条记录格式如下：

```json
{
  "date": "2025-11-03",
  "user_id": "zhangsan",
  "new_contacts": 12,
  "deleted_by_user": 3,
  "stat_time": 1762214400,
  "retrieved_at": "2025-11-04T09:15:33+08:00",
  "raw_metrics": {
    "stat_time": 1762214400,
    "userid": "zhangsan",
    "new_contact_cnt": 12,
    "negative_feedback_cnt": 3,
    "chat_cnt": 48,
    "message_cnt": 120
  }
}
```

- `new_contacts`：当天新增的外部联系人数量。
- `deleted_by_user`：当天客户主动删除或其他负反馈的总数（接口字段 `customer_contact_del_cnt` 或 `negative_feedback_cnt` 等）。
- `raw_metrics`：企业微信接口返回的原始数据，方便后续扩展其它指标。

## 运行机制说明

1. 通过 `corp_id` 和 `corp_secret` 获取 `access_token`，自动缓存并在过期前刷新。
2. 调用 `externalcontact/get_user_behavior_data` 接口，按日获取员工的客户联系数据统计。
3. 解析返回值中的 `new_contact_cnt`、`customer_contact_del_cnt`（或 `negative_feedback_cnt`）等字段。
4. 对于接口未返回的员工补写零值，保证每天都有完整记录。
5. 将结果按（日期，员工）维度去重写入 JSON 文件。

## 注意事项

- 接口单次最多支持 100 个 `userid`，工具已经自动分批调用。
- 企业微信后台数据存在统计延迟，建议在每天早晨定时执行上一日的数据采集。
- 「被客户删除」指标依赖接口返回字段：
  - 首选 `customer_contact_del_cnt` 或 `customer_contact_delete_cnt`
  - 若不存在，则退回 `negative_feedback_cnt`，代表客户删除或投诉等负反馈行为。
- 若需长期保存或深度分析，可将 JSON 数据导入到 MongoDB、SQL 或 BI 工具中。

## 常见问题

| 问题 | 解决方案 |
|------|-----------|
| `WeCom API error 40014` | access_token 失效，工具会自动重试。检查 `corp_id`/`corp_secret` 是否正确。 |
| `配置文件不存在` | 确认 `--config` 指向的文件路径存在。 |
| 没有生成数据 | 检查配置的 `userid` 是否具备客户联系权限，或当天确实无新增/删除数据。 |
| 想要部署成定时任务 | 可结合 `crontab` 或 CI/CD 定时执行 `collect` 命令，并将日志输出到文件。 |

## 后续扩展建议

- 将数据直接写入 MongoDB / MySQL，实现多维分析和看板展示。
- 对接消息通知（如企业微信自建应用、飞书 Webhook 等）推送每日统计快报。
- 结合「客户群」统计接口，获取群聊维度的新增与流失数据。

欢迎根据企业内部需求二次开发，如有新的字段或接口需要支持，可在 `WeComFriendTracker.DELETE_CONTACT_KEYS` / `NEW_CONTACT_KEYS` 中扩展即可。
