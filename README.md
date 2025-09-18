# 直播间管理系统

一个完整的线下直播间管理程序，支持预约管理、门禁控制、使用时长监控等功能。

## 功能特性

### 核心功能
- **预约管理**: 用户可以预约特定时间段的直播间使用
- **门禁控制**: 基于预约时间自动控制门禁开关
- **时长监控**: 实时监控直播间使用时长
- **自动锁门**: 预约结束后自动锁定门禁
- **访问日志**: 记录所有门禁操作和访问记录

### 技术特性
- **实时监控**: 30秒自动刷新状态
- **硬件模拟**: 内置门禁硬件模拟器
- **Web界面**: 现代化的响应式管理界面
- **RESTful API**: 完整的后端API接口
- **定时任务**: 自动处理预约时间验证

## 系统架构

```
直播间管理系统
├── 前端界面 (HTML/CSS/JavaScript)
├── 后端API (Flask)
├── 数据库 (SQLite)
├── 门禁控制 (硬件模拟)
└── 定时任务 (预约管理)
```

## 安装和运行

### 环境要求
- Python 3.7+
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

### 初始化数据库
```bash
python run.py --init-db
```

### 启动系统
```bash
python run.py
```

### 启动选项
```bash
python run.py --help
```

选项说明：
- `--host`: 服务器地址 (默认: 0.0.0.0)
- `--port`: 服务器端口 (默认: 5000)
- `--debug`: 启用调试模式
- `--no-hardware`: 禁用硬件模拟
- `--init-db`: 初始化数据库

## 使用说明

### 1. 访问系统
打开浏览器访问: `http://localhost:5000`

### 2. 创建预约
1. 点击"新建预约"按钮
2. 选择房间、填写用户信息
3. 设置开始和结束时间
4. 提交预约

### 3. 门禁控制
- **自动控制**: 系统会根据预约时间自动开关门禁
- **手动控制**: 可以手动锁定/解锁门禁
- **访问验证**: 用户可以通过手机号验证访问权限

### 4. 监控管理
- 实时查看房间状态
- 监控预约列表
- 查看访问日志

## API接口

### 房间管理
- `GET /api/rooms` - 获取房间列表
- `POST /api/rooms` - 创建房间

### 预约管理
- `GET /api/bookings` - 获取预约列表
- `POST /api/bookings` - 创建预约
- `PUT /api/bookings/<id>` - 更新预约状态

### 门禁控制
- `POST /api/access/<room_id>` - 验证访问权限
- `POST /api/door/<room_id>/lock` - 锁定门禁
- `POST /api/door/<room_id>/unlock` - 解锁门禁

### 日志查询
- `GET /api/logs` - 获取访问日志

## 配置说明

系统配置文件位于 `config.py`，主要配置项：

- `DOOR_UNLOCK_DURATION`: 门禁解锁持续时间（秒）
- `AUTO_LOCK_DELAY`: 预约结束后自动锁门延迟（秒）
- `MAX_BOOKING_DURATION`: 最大预约时长（分钟）
- `MIN_BOOKING_DURATION`: 最小预约时长（分钟）

## 硬件接口

系统包含硬件模拟器 (`hardware_simulator.py`)，模拟真实门禁设备：

- 门锁控制
- 运动传感器
- 门开关传感器
- 紧急按钮
- 断电检测

## 数据库结构

### 房间表 (Room)
- id: 房间ID
- name: 房间名称
- is_locked: 门禁状态
- current_session: 当前会话ID

### 预约表 (Booking)
- id: 预约ID
- room_id: 房间ID
- user_name: 用户姓名
- user_phone: 用户手机号
- start_time: 开始时间
- end_time: 结束时间
- status: 预约状态
- actual_start_time: 实际开始时间
- actual_end_time: 实际结束时间

### 访问日志表 (AccessLog)
- id: 日志ID
- room_id: 房间ID
- booking_id: 预约ID
- action: 操作类型
- timestamp: 时间戳
- reason: 操作原因

## 开发说明

### 项目结构
```
/workspace
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── hardware_simulator.py # 硬件模拟器
├── run.py               # 启动脚本
├── requirements.txt     # 依赖包
├── templates/           # HTML模板
│   └── index.html
├── static/             # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── README.md           # 说明文档
```

### 扩展开发
1. 添加新的API接口
2. 扩展硬件接口支持
3. 增加用户认证功能
4. 添加通知功能
5. 集成真实硬件设备

## 故障排除

### 常见问题
1. **端口被占用**: 修改 `--port` 参数
2. **数据库错误**: 删除 `livestream_management.db` 重新初始化
3. **硬件模拟问题**: 使用 `--no-hardware` 参数禁用

### 日志查看
系统日志保存在 `livestream_management.log` 文件中。

## 许可证

MIT License