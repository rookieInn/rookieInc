#!/usr/bin/env python3
"""
Chrome书签同步使用示例
"""

from chrome_to_edge_sync import BookmarkSync
import time

def example_manual_sync():
    """示例：手动同步一次"""
    print("=== 手动同步示例 ===")
    
    # 创建同步器
    sync = BookmarkSync()
    
    # 运行一次同步
    success = sync.run_once()
    
    if success:
        print("✓ 手动同步成功")
    else:
        print("✗ 手动同步失败")

def example_custom_config():
    """示例：使用自定义配置"""
    print("\n=== 自定义配置示例 ===")
    
    # 创建自定义配置
    custom_config = {
        "sync_interval_minutes": 60,  # 每小时同步一次
        "backup_enabled": True,
        "backup_retention_days": 14,  # 保留14天备份
        "exclude_folders": ["书签栏", "其他书签", "工作书签"],
        "log_level": "DEBUG"
    }
    
    # 保存自定义配置
    import json
    with open('/workspace/custom_config.json', 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, indent=4, ensure_ascii=False)
    
    # 使用自定义配置创建同步器
    sync = BookmarkSync('/workspace/custom_config.json')
    
    print("✓ 自定义配置已创建")
    print(f"同步间隔: {sync.config['sync_interval_minutes']}分钟")
    print(f"备份保留: {sync.config['backup_retention_days']}天")
    print(f"排除文件夹: {sync.config['exclude_folders']}")

def example_scheduled_sync():
    """示例：启动定期同步（运行10秒后停止）"""
    print("\n=== 定期同步示例 ===")
    print("启动定期同步，10秒后自动停止...")
    
    sync = BookmarkSync()
    
    # 修改同步间隔为10秒（仅用于演示）
    sync.config['sync_interval_minutes'] = 0.1  # 6秒
    
    # 在单独线程中启动调度器
    import threading
    scheduler_thread = threading.Thread(target=sync.start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # 运行10秒
    time.sleep(10)
    
    print("✓ 定期同步示例完成")

def main():
    """主函数"""
    print("Chrome书签同步使用示例")
    print("=" * 50)
    
    # 示例1：手动同步
    example_manual_sync()
    
    # 示例2：自定义配置
    example_custom_config()
    
    # 示例3：定期同步（演示）
    # example_scheduled_sync()  # 取消注释以运行
    
    print("\n所有示例完成！")
    print("\n实际使用方法：")
    print("1. 手动同步: python3 chrome_to_edge_sync.py --once")
    print("2. 定期同步: python3 chrome_to_edge_sync.py")
    print("3. 简化版本: python3 bookmark_sync_manual.py")

if __name__ == "__main__":
    main()