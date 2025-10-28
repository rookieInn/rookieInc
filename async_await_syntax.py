#!/usr/bin/env python3
"""
Python async/await 语法详解
演示async/await关键字的使用方法和最佳实践
"""

import asyncio
import time
from typing import Any, List


# 1. async def 定义协程函数
async def basic_async_function():
    """使用 async def 定义协程函数"""
    print("这是一个协程函数")
    return "协程返回值"


# 2. await 关键字的使用
async def await_examples():
    """演示 await 关键字的各种用法"""
    print("\n=== await 关键字示例 ===")
    
    # await 用于等待其他协程
    result1 = await basic_async_function()
    print(f"等待协程结果: {result1}")
    
    # await 用于等待 asyncio.sleep
    print("开始等待...")
    await asyncio.sleep(1)
    print("等待结束")
    
    # await 用于等待多个协程
    async def task1():
        await asyncio.sleep(0.5)
        return "任务1完成"
    
    async def task2():
        await asyncio.sleep(1.0)
        return "任务2完成"
    
    # 顺序等待（串行）
    start_time = time.time()
    result1 = await task1()
    result2 = await task2()
    end_time = time.time()
    
    print(f"串行执行结果: {result1}, {result2}")
    print(f"串行执行时间: {end_time - start_time:.2f}秒")


# 3. 协程中的异常处理
async def exception_handling():
    """协程中的异常处理"""
    print("\n=== 协程异常处理 ===")
    
    async def risky_coroutine():
        await asyncio.sleep(0.5)
        raise ValueError("协程中发生错误")
    
    try:
        await risky_coroutine()
    except ValueError as e:
        print(f"捕获到协程异常: {e}")


# 4. 协程返回值
async def return_values():
    """演示协程的返回值"""
    print("\n=== 协程返回值 ===")
    
    async def calculate_sum(a: int, b: int):
        await asyncio.sleep(0.1)  # 模拟计算时间
        return a + b
    
    async def calculate_product(a: int, b: int):
        await asyncio.sleep(0.1)
        return a * b
    
    # 获取协程返回值
    sum_result = await calculate_sum(10, 20)
    product_result = await calculate_product(3, 4)
    
    print(f"求和结果: {sum_result}")
    print(f"乘积结果: {product_result}")


# 5. 协程中的循环和条件
async def control_structures():
    """协程中的控制结构"""
    print("\n=== 协程控制结构 ===")
    
    # for 循环
    for i in range(3):
        print(f"循环迭代 {i}")
        await asyncio.sleep(0.2)
    
    # while 循环
    counter = 0
    while counter < 3:
        print(f"while 循环: {counter}")
        await asyncio.sleep(0.2)
        counter += 1
    
    # 条件语句
    async def conditional_task(condition: bool):
        if condition:
            print("条件为真，执行任务A")
            await asyncio.sleep(0.3)
            return "任务A完成"
        else:
            print("条件为假，执行任务B")
            await asyncio.sleep(0.3)
            return "任务B完成"
    
    result1 = await conditional_task(True)
    result2 = await conditional_task(False)
    print(f"条件结果1: {result1}")
    print(f"条件结果2: {result2}")


# 6. 嵌套协程
async def nested_coroutines():
    """嵌套协程示例"""
    print("\n=== 嵌套协程 ===")
    
    async def inner_coroutine(name: str):
        print(f"内部协程 {name} 开始")
        await asyncio.sleep(0.5)
        print(f"内部协程 {name} 结束")
        return f"内部协程 {name} 的返回值"
    
    async def outer_coroutine():
        print("外部协程开始")
        
        # 调用内部协程
        result1 = await inner_coroutine("A")
        result2 = await inner_coroutine("B")
        
        print("外部协程结束")
        return [result1, result2]
    
    results = await outer_coroutine()
    print(f"嵌套协程结果: {results}")


# 7. 协程中的生成器
async def coroutine_generators():
    """协程生成器"""
    print("\n=== 协程生成器 ===")
    
    async def async_generator(n: int):
        """异步生成器函数"""
        for i in range(n):
            print(f"生成值: {i}")
            await asyncio.sleep(0.3)
            yield i * 2
    
    # 使用异步生成器
    async for value in async_generator(3):
        print(f"接收到生成的值: {value}")


# 8. 协程装饰器
def coroutine_decorator(func):
    """协程装饰器"""
    def wrapper(*args, **kwargs):
        print(f"装饰器: 准备执行 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@coroutine_decorator
async def decorated_coroutine():
    """被装饰的协程"""
    print("执行被装饰的协程")
    await asyncio.sleep(0.5)
    return "装饰器协程完成"


# 9. 协程类方法
class AsyncClass:
    """包含协程方法的类"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def async_method(self):
        """异步方法"""
        print(f"异步方法 {self.name} 开始执行")
        await asyncio.sleep(0.5)
        print(f"异步方法 {self.name} 执行完成")
        return f"异步方法 {self.name} 的返回值"
    
    @classmethod
    async def async_class_method(cls):
        """异步类方法"""
        print("异步类方法执行")
        await asyncio.sleep(0.3)
        return "异步类方法完成"
    
    @staticmethod
    async def async_static_method():
        """异步静态方法"""
        print("异步静态方法执行")
        await asyncio.sleep(0.3)
        return "异步静态方法完成"


# 10. 协程最佳实践
async def best_practices():
    """协程最佳实践示例"""
    print("\n=== 协程最佳实践 ===")
    
    # 1. 使用 asyncio.gather 进行并发
    async def task(name: str, delay: float):
        print(f"任务 {name} 开始")
        await asyncio.sleep(delay)
        print(f"任务 {name} 完成")
        return f"任务 {name} 结果"
    
    # 并发执行多个任务
    tasks = [
        task("A", 1.0),
        task("B", 1.5),
        task("C", 2.0)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"并发执行结果: {results}")
    print(f"并发执行时间: {end_time - start_time:.2f}秒")
    
    # 2. 使用 asyncio.create_task 创建任务
    print("\n使用 create_task:")
    task1 = asyncio.create_task(task("Task1", 1.0))
    task2 = asyncio.create_task(task("Task2", 1.5))
    
    # 可以在这里做其他工作
    print("在等待任务完成时可以做其他工作")
    
    # 等待任务完成
    result1 = await task1
    result2 = await task2
    print(f"Task 结果: {result1}, {result2}")


# 主函数
async def main():
    """主函数"""
    print("Python async/await 语法详解")
    print("=" * 50)
    
    # 运行所有示例
    await await_examples()
    await exception_handling()
    await return_values()
    await control_structures()
    await nested_coroutines()
    await coroutine_generators()
    
    # 装饰器示例
    print("\n=== 协程装饰器 ===")
    result = await decorated_coroutine()
    print(f"装饰器结果: {result}")
    
    # 类方法示例
    print("\n=== 协程类方法 ===")
    obj = AsyncClass("测试对象")
    method_result = await obj.async_method()
    print(f"实例方法结果: {method_result}")
    
    class_result = await AsyncClass.async_class_method()
    print(f"类方法结果: {class_result}")
    
    static_result = await AsyncClass.async_static_method()
    print(f"静态方法结果: {static_result}")
    
    # 最佳实践
    await best_practices()


if __name__ == "__main__":
    asyncio.run(main())