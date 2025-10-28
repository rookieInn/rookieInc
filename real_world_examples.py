#!/usr/bin/env python3
"""
Python协程实际应用场景示例
演示协程在真实项目中的应用场景和最佳实践
"""

import asyncio
import time
import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiofiles
import aiohttp


# 1. 网络爬虫示例
@dataclass
class WebPage:
    url: str
    title: str
    content: str
    status_code: int
    fetch_time: float


class AsyncWebCrawler:
    """异步网络爬虫"""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> WebPage:
        """获取单个页面"""
        async with self.semaphore:
            start_time = time.time()
            try:
                # 模拟网络请求（实际项目中这里会是真实的HTTP请求）
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # 模拟页面内容
                content = f"这是来自 {url} 的页面内容"
                title = f"页面标题 - {url.split('/')[-1]}"
                
                return WebPage(
                    url=url,
                    title=title,
                    content=content,
                    status_code=200,
                    fetch_time=time.time() - start_time
                )
            except Exception as e:
                return WebPage(
                    url=url,
                    title="错误页面",
                    content=str(e),
                    status_code=500,
                    fetch_time=time.time() - start_time
                )
    
    async def crawl_pages(self, urls: List[str]) -> List[WebPage]:
        """并发爬取多个页面"""
        tasks = [self.fetch_page(url) for url in urls]
        return await asyncio.gather(*tasks)


# 2. 数据库操作示例
class AsyncDatabase:
    """模拟异步数据库操作"""
    
    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()
    
    async def insert(self, table: str, record: Dict[str, Any]) -> str:
        """插入记录"""
        async with self.lock:
            record_id = f"{table}_{len(self.data) + 1}"
            record['id'] = record_id
            record['created_at'] = datetime.now().isoformat()
            self.data[record_id] = record
            await asyncio.sleep(0.1)  # 模拟数据库延迟
            return record_id
    
    async def select(self, table: str, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """查询记录"""
        await asyncio.sleep(0.2)  # 模拟查询延迟
        results = []
        for record in self.data.values():
            if record.get('table') == table:
                if conditions is None or all(record.get(k) == v for k, v in conditions.items()):
                    results.append(record)
        return results
    
    async def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """更新记录"""
        async with self.lock:
            if record_id in self.data:
                self.data[record_id].update(updates)
                self.data[record_id]['updated_at'] = datetime.now().isoformat()
                await asyncio.sleep(0.1)
                return True
            return False
    
    async def delete(self, record_id: str) -> bool:
        """删除记录"""
        async with self.lock:
            if record_id in self.data:
                del self.data[record_id]
                await asyncio.sleep(0.1)
                return True
            return False


# 3. 文件处理示例
class AsyncFileProcessor:
    """异步文件处理器"""
    
    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件"""
        # 模拟文件读取和处理
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # 模拟文件分析
        file_size = random.randint(1000, 10000)
        line_count = random.randint(50, 500)
        
        return {
            "file_path": file_path,
            "size": file_size,
            "line_count": line_count,
            "processed_at": datetime.now().isoformat(),
            "status": "success"
        }
    
    async def batch_process_files(self, file_paths: List[str], batch_size: int = 5) -> List[Dict[str, Any]]:
        """批量处理文件"""
        results = []
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            batch_tasks = [self.process_file(path) for path in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            print(f"已处理批次 {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        return results


# 4. API服务示例
class AsyncAPIService:
    """异步API服务"""
    
    def __init__(self):
        self.db = AsyncDatabase()
        self.request_count = 0
        self.lock = asyncio.Lock()
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理API请求"""
        async with self.lock:
            self.request_count += 1
            request_id = f"req_{self.request_count}"
        
        # 模拟请求处理
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # 根据请求类型处理
        request_type = request_data.get('type', 'unknown')
        
        if request_type == 'create':
            record_id = await self.db.insert('users', request_data.get('data', {}))
            return {"status": "success", "id": record_id}
        
        elif request_type == 'read':
            results = await self.db.select('users', request_data.get('conditions', {}))
            return {"status": "success", "data": results}
        
        elif request_type == 'update':
            success = await self.db.update(
                request_data.get('id'),
                request_data.get('updates', {})
            )
            return {"status": "success" if success else "failed"}
        
        else:
            return {"status": "error", "message": "Unknown request type"}


# 5. 实时数据处理示例
class AsyncDataProcessor:
    """异步数据处理器"""
    
    def __init__(self):
        self.data_queue = asyncio.Queue()
        self.processed_count = 0
        self.running = False
    
    async def data_producer(self, data_source: str, count: int):
        """数据生产者"""
        for i in range(count):
            data = {
                "id": f"{data_source}_{i}",
                "timestamp": datetime.now().isoformat(),
                "value": random.randint(1, 100),
                "source": data_source
            }
            await self.data_queue.put(data)
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # 发送结束信号
        await self.data_queue.put(None)
    
    async def data_consumer(self, consumer_id: int):
        """数据消费者"""
        while self.running:
            try:
                data = await asyncio.wait_for(self.data_queue.get(), timeout=1.0)
                if data is None:
                    break
                
                # 处理数据
                await self.process_data(data, consumer_id)
                self.data_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
    
    async def process_data(self, data: Dict[str, Any], consumer_id: int):
        """处理单个数据项"""
        # 模拟数据处理
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # 模拟数据转换
        processed_data = {
            **data,
            "processed_by": consumer_id,
            "processed_at": datetime.now().isoformat(),
            "processed_value": data["value"] * 2
        }
        
        self.processed_count += 1
        print(f"消费者 {consumer_id} 处理数据: {processed_data['id']}")
    
    async def start_processing(self, data_sources: List[str], consumer_count: int = 3):
        """开始数据处理"""
        self.running = True
        
        # 启动消费者
        consumers = [
            asyncio.create_task(self.data_consumer(i))
            for i in range(consumer_count)
        ]
        
        # 启动生产者
        producers = [
            asyncio.create_task(self.data_producer(source, 10))
            for source in data_sources
        ]
        
        # 等待所有生产者完成
        await asyncio.gather(*producers)
        
        # 等待队列为空
        await self.data_queue.join()
        
        # 停止消费者
        self.running = False
        for consumer in consumers:
            consumer.cancel()
        
        print(f"数据处理完成，共处理 {self.processed_count} 条数据")


# 6. 微服务通信示例
class AsyncMicroservice:
    """异步微服务"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.health_status = "healthy"
        self.request_handlers = {}
    
    def register_handler(self, endpoint: str, handler):
        """注册请求处理器"""
        self.request_handlers[endpoint] = handler
    
    async def handle_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        if endpoint not in self.request_handlers:
            return {"error": "Endpoint not found"}
        
        handler = self.request_handlers[endpoint]
        return await handler(data)
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        await asyncio.sleep(0.1)  # 模拟检查时间
        return {
            "service": self.service_name,
            "status": self.health_status,
            "timestamp": datetime.now().isoformat()
        }


# 7. 缓存系统示例
class AsyncCache:
    """异步缓存系统"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if time.time() < item['expires_at']:
                    return item['value']
                else:
                    del self.cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        async with self.lock:
            ttl = ttl or self.default_ttl
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """清空缓存"""
        async with self.lock:
            self.cache.clear()


# 8. 综合应用示例
async def comprehensive_example():
    """综合应用示例"""
    print("\n=== 综合应用示例 ===")
    
    # 1. 网络爬虫
    print("1. 网络爬虫示例:")
    urls = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com",
        "https://example4.com",
        "https://example5.com"
    ]
    
    async with AsyncWebCrawler(max_concurrent=3) as crawler:
        pages = await crawler.crawl_pages(urls)
        for page in pages:
            print(f"页面: {page.url} - 状态: {page.status_code} - 耗时: {page.fetch_time:.2f}s")
    
    # 2. 数据库操作
    print("\n2. 数据库操作示例:")
    db = AsyncDatabase()
    
    # 批量插入用户
    users = [
        {"name": f"用户{i}", "email": f"user{i}@example.com", "table": "users"}
        for i in range(5)
    ]
    
    insert_tasks = [db.insert("users", user) for user in users]
    user_ids = await asyncio.gather(*insert_tasks)
    print(f"插入的用户ID: {user_ids}")
    
    # 查询用户
    all_users = await db.select("users")
    print(f"查询到 {len(all_users)} 个用户")
    
    # 3. 文件处理
    print("\n3. 文件处理示例:")
    file_processor = AsyncFileProcessor()
    file_paths = [f"file_{i}.txt" for i in range(8)]
    
    processed_files = await file_processor.batch_process_files(file_paths, batch_size=3)
    print(f"处理了 {len(processed_files)} 个文件")
    
    # 4. API服务
    print("\n4. API服务示例:")
    api_service = AsyncAPIService()
    
    # 模拟API请求
    requests = [
        {"type": "create", "data": {"name": "新用户", "email": "new@example.com"}},
        {"type": "read", "conditions": {"name": "用户1"}},
        {"type": "update", "id": user_ids[0], "updates": {"name": "更新后的用户1"}}
    ]
    
    request_tasks = [api_service.handle_request(req) for req in requests]
    responses = await asyncio.gather(*request_tasks)
    
    for i, response in enumerate(responses):
        print(f"请求 {i+1} 响应: {response}")
    
    # 5. 实时数据处理
    print("\n5. 实时数据处理示例:")
    data_processor = AsyncDataProcessor()
    data_sources = ["sensor1", "sensor2", "sensor3"]
    
    await data_processor.start_processing(data_sources, consumer_count=2)
    
    # 6. 微服务通信
    print("\n6. 微服务通信示例:")
    
    # 创建用户服务
    user_service = AsyncMicroservice("user-service")
    user_service.register_handler("get_user", lambda data: {"user_id": data.get("id"), "name": "测试用户"})
    
    # 创建订单服务
    order_service = AsyncMicroservice("order-service")
    order_service.register_handler("create_order", lambda data: {"order_id": "12345", "status": "created"})
    
    # 并发调用微服务
    service_tasks = [
        user_service.handle_request("get_user", {"id": "123"}),
        order_service.handle_request("create_order", {"user_id": "123", "product": "测试产品"}),
        user_service.health_check(),
        order_service.health_check()
    ]
    
    service_responses = await asyncio.gather(*service_tasks)
    for response in service_responses:
        print(f"微服务响应: {response}")
    
    # 7. 缓存系统
    print("\n7. 缓存系统示例:")
    cache = AsyncCache(default_ttl=60)
    
    # 设置缓存
    await cache.set("user:123", {"name": "缓存用户", "id": 123})
    await cache.set("config:app", {"theme": "dark", "language": "zh"})
    
    # 获取缓存
    user_data = await cache.get("user:123")
    config_data = await cache.get("config:app")
    non_existent = await cache.get("non:existent")
    
    print(f"用户缓存: {user_data}")
    print(f"配置缓存: {config_data}")
    print(f"不存在的缓存: {non_existent}")


# 主函数
async def main():
    """主函数"""
    print("Python协程实际应用场景示例")
    print("=" * 50)
    
    # 运行综合示例
    await comprehensive_example()


if __name__ == "__main__":
    asyncio.run(main())