#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户图片清理系统使用示例
演示如何使用各个组件进行图片管理
"""

import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_image_models import UserImageDatabase, UserImage

def example_database_operations():
    """演示数据库操作"""
    print("=" * 60)
    print("数据库操作示例")
    print("=" * 60)
    
    # 创建数据库实例
    db = UserImageDatabase()
    
    # 模拟用户上传图片
    user_id = "demo_user_001"
    print(f"模拟用户 {user_id} 上传图片...")
    
    # 上传15张图片（超过限制）
    for i in range(15):
        image = UserImage(
            id=None,
            user_id=user_id,
            image_name=f"vacation_photo_{i+1:02d}.jpg",
            oss_key=f"users/{user_id}/vacation_photo_{i+1:02d}.jpg",
            file_size=2048000 + i * 50000,  # 2MB + 变化
            mime_type="image/jpeg",
            upload_time=datetime.now() - timedelta(hours=i),
            last_accessed=None
        )
        
        success = db.add_user_image(image)
        if success:
            print(f"  ✅ 上传图片: {image.image_name} ({image.file_size/1024/1024:.1f}MB)")
        else:
            print(f"  ❌ 上传失败: {image.image_name}")
    
    # 查看用户当前图片
    print(f"\n用户 {user_id} 当前图片:")
    images = db.get_user_images(user_id)
    for img in images:
        print(f"  📷 {img.image_name} - {img.file_size/1024/1024:.1f}MB - {img.upload_time.strftime('%Y-%m-%d %H:%M')}")
    
    # 查看统计信息
    stats = db.get_user_image_stats(user_id)
    print(f"\n统计信息:")
    print(f"  总图片数: {stats['total_images']}")
    print(f"  活跃图片数: {stats['active_images']}")
    print(f"  总存储大小: {stats['total_size_mb']:.1f}MB")
    print(f"  首次上传: {stats['first_upload']}")
    print(f"  最后上传: {stats['last_upload']}")
    
    # 查看待删除的图片
    images_to_delete = db.get_images_to_delete(0)  # 立即删除
    print(f"\n待删除图片数量: {len(images_to_delete)}")
    for img_id, oss_key in images_to_delete[:5]:  # 只显示前5个
        print(f"  🗑️ {oss_key}")
    
    db.close()
    print("\n✅ 数据库操作示例完成")

def example_cleanup_simulation():
    """演示清理过程模拟"""
    print("=" * 60)
    print("清理过程模拟")
    print("=" * 60)
    
    # 创建数据库实例
    db = UserImageDatabase()
    
    # 获取待删除的图片
    images_to_delete = db.get_images_to_delete(0)
    
    if not images_to_delete:
        print("没有需要删除的图片")
        return
    
    print(f"找到 {len(images_to_delete)} 张需要删除的图片")
    
    # 模拟删除过程
    deleted_count = 0
    for i, (img_id, oss_key) in enumerate(images_to_delete[:10], 1):  # 只处理前10个
        print(f"处理 {i}/{min(10, len(images_to_delete))}: {oss_key}")
        
        # 模拟OSS文件删除
        print(f"  🗑️ 删除OSS文件: {oss_key}")
        
        # 删除数据库记录
        if db.delete_image_record(img_id):
            print(f"  ✅ 删除数据库记录: ID={img_id}")
            deleted_count += 1
        else:
            print(f"  ❌ 删除数据库记录失败: ID={img_id}")
    
    print(f"\n清理完成: 成功删除 {deleted_count} 张图片")
    
    # 查看清理后的统计
    stats = db.get_user_image_stats()
    print(f"\n清理后统计:")
    print(f"  总用户数: {stats['total_users']}")
    print(f"  总图片数: {stats['total_images']}")
    print(f"  活跃图片数: {stats['active_images']}")
    print(f"  总存储大小: {stats['total_size_mb']:.1f}MB")
    
    db.close()
    print("\n✅ 清理过程模拟完成")

def example_multiple_users():
    """演示多用户场景"""
    print("=" * 60)
    print("多用户场景示例")
    print("=" * 60)
    
    # 创建数据库实例
    db = UserImageDatabase()
    
    # 模拟多个用户上传图片
    users = ["alice", "bob", "charlie"]
    
    for user_id in users:
        print(f"\n用户 {user_id} 上传图片:")
        
        # 每个用户上传不同数量的图片
        num_images = 8 if user_id == "alice" else 12 if user_id == "bob" else 15
        
        for i in range(num_images):
            image = UserImage(
                id=None,
                user_id=user_id,
                image_name=f"{user_id}_photo_{i+1:02d}.jpg",
                oss_key=f"users/{user_id}/{user_id}_photo_{i+1:02d}.jpg",
                file_size=1500000 + i * 10000,
                mime_type="image/jpeg",
                upload_time=datetime.now() - timedelta(hours=i),
                last_accessed=None
            )
            
            db.add_user_image(image)
            print(f"  📷 {image.image_name}")
        
        # 查看用户图片数量
        images = db.get_user_images(user_id)
        print(f"  当前活跃图片数: {len(images)}")
    
    # 查看总体统计
    print(f"\n总体统计:")
    stats = db.get_user_image_stats()
    print(f"  总用户数: {stats['total_users']}")
    print(f"  总图片数: {stats['total_images']}")
    print(f"  活跃图片数: {stats['active_images']}")
    print(f"  平均图片大小: {stats['avg_size_mb']:.1f}MB")
    
    # 查看各用户统计
    for user_id in users:
        user_stats = db.get_user_image_stats(user_id)
        print(f"\n用户 {user_id}:")
        print(f"  活跃图片数: {user_stats['active_images']}")
        print(f"  总存储大小: {user_stats['total_size_mb']:.1f}MB")
    
    db.close()
    print("\n✅ 多用户场景示例完成")

def main():
    """主函数"""
    print("用户图片清理系统使用示例")
    print("=" * 60)
    
    try:
        # 运行各个示例
        example_database_operations()
        print()
        
        example_cleanup_simulation()
        print()
        
        example_multiple_users()
        print()
        
        print("=" * 60)
        print("🎉 所有示例运行完成！")
        print("=" * 60)
        
        print("\n💡 提示:")
        print("1. 每个用户最多保留10张图片（可配置）")
        print("2. 超出限制的图片会被标记为不活跃")
        print("3. 可以设置延迟时间后再实际删除")
        print("4. 支持批量处理和重试机制")
        print("5. 提供详细的统计信息和日志记录")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()