# Python协程使用指南

本仓库包含了Python协程的完整使用示例和最佳实践，涵盖了从基础概念到实际应用的各个方面。

## 文件说明

### 1. `coroutine_basics.py` - 协程基础
- 协程函数定义和基本用法
- `async`/`await` 关键字使用
- 协程并发执行
- 异常处理和超时控制
- 协程生成器和同步原语

### 2. `async_await_syntax.py` - async/await语法详解
- `async def` 定义协程函数
- `await` 关键字的各种用法
- 协程中的控制结构（循环、条件）
- 嵌套协程和协程装饰器
- 协程类方法和最佳实践

### 3. `concurrent_coroutines.py` - 协程并发执行
- 基础并发示例
- `asyncio.gather` 的不同使用方式
- `asyncio.create_task` 创建任务
- 任务取消和超时控制
- 协程池和限制并发数
- 生产者-消费者模式
- 协程间通信和性能对比

### 4. `asyncio_tools.py` - asyncio工具详解
- `asyncio.gather` 详细用法和高级特性
- `asyncio.create_task` 任务管理
- 任务组合模式和错误处理
- 性能优化技巧
- 重试机制和批量处理

### 5. `real_world_examples.py` - 实际应用场景
- 网络爬虫实现
- 异步数据库操作
- 文件批量处理
- API服务开发
- 实时数据处理
- 微服务通信
- 缓存系统实现

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行示例
```bash
# 运行基础协程示例
python coroutine_basics.py

# 运行async/await语法示例
python async_await_syntax.py

# 运行并发协程示例
python concurrent_coroutines.py

# 运行asyncio工具示例
python asyncio_tools.py

# 运行实际应用示例
python real_world_examples.py
```

## 核心概念

### 1. 协程函数
```python
async def my_coroutine():
    print("这是一个协程函数")
    await asyncio.sleep(1)
    return "协程返回值"
```

### 2. 并发执行
```python
# 使用 asyncio.gather 并发执行
tasks = [my_coroutine() for _ in range(5)]
results = await asyncio.gather(*tasks)

# 使用 asyncio.create_task 创建任务
task = asyncio.create_task(my_coroutine())
result = await task
```

### 3. 异常处理
```python
try:
    result = await risky_coroutine()
except ValueError as e:
    print(f"捕获异常: {e}")

# 使用 return_exceptions=True
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 4. 超时控制
```python
try:
    result = await asyncio.wait_for(slow_coroutine(), timeout=5.0)
except asyncio.TimeoutError:
    print("操作超时")
```

## 最佳实践

### 1. 使用信号量限制并发
```python
semaphore = asyncio.Semaphore(10)
async def limited_task():
    async with semaphore:
        # 执行任务
        pass
```

### 2. 合理使用 asyncio.gather 和 create_task
- 使用 `gather` 等待多个协程完成
- 使用 `create_task` 在协程运行时创建新任务

### 3. 错误处理和重试
```python
async def retry_task(max_retries=3):
    for attempt in range(max_retries):
        try:
            return await unreliable_task()
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (attempt + 1))
            else:
                raise e
```

### 4. 资源管理
```python
async def resource_manager():
    async with aiohttp.ClientSession() as session:
        # 使用session
        pass
```

## 常见问题

### Q: 什么时候使用协程？
A: 协程适用于IO密集型任务，如网络请求、文件操作、数据库查询等。对于CPU密集型任务，协程的优势不明显。

### Q: 协程和线程有什么区别？
A: 协程是单线程的，通过协作式多任务实现并发；线程是抢占式多任务。协程更轻量级，但需要显式让出控制权。

### Q: 如何调试协程？
A: 可以使用 `asyncio.run()` 运行协程，使用 `pdb` 或 `ipdb` 进行调试，注意在 `await` 语句处设置断点。

### Q: 协程中的全局变量安全吗？
A: 协程是单线程的，所以全局变量是安全的，但要注意异步操作可能导致的竞态条件。

## 性能优化

### 1. 批量处理
```python
async def batch_process(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        tasks = [process_item(item) for item in batch]
        await asyncio.gather(*tasks)
```

### 2. 连接池
```python
# 使用连接池复用连接
async with aiohttp.ClientSession() as session:
    tasks = [session.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
```

### 3. 缓存机制
```python
cache = {}
async def cached_operation(key):
    if key not in cache:
        cache[key] = await expensive_operation()
    return cache[key]
```

## 扩展阅读

- [Python asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)
- [aiohttp 文档](https://docs.aiohttp.org/)
- [异步编程最佳实践](https://docs.python.org/3/library/asyncio-dev.html)

## 许可证

MIT License