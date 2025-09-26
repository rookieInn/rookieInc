#!/usr/bin/env python3
"""
旅游路线规划智能体启动脚本
"""

import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    # 检查环境变量
    required_vars = ["SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"警告: 缺少环境变量 {missing_vars}")
        print("请复制 .env.example 到 .env 并填写必要的配置")
    
    # 启动应用
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )