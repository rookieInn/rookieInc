#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户图片数据模型和数据库操作类
功能：
1. 管理用户图片记录
2. 支持每个用户最多保留10张图片
3. 自动清理多余的图片记录和OSS文件
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from configparser import ConfigParser
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserImage:
    """用户图片数据模型"""
    id: Optional[int]
    user_id: str
    image_name: str
    oss_key: str  # OSS中的文件路径/键名
    file_size: int  # 文件大小（字节）
    mime_type: str  # 文件类型
    upload_time: datetime
    last_accessed: Optional[datetime]
    is_active: bool = True  # 是否活跃（未被删除）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['upload_time'] = self.upload_time.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data

class UserImageDatabase:
    """用户图片数据库操作类"""
    
    def __init__(self, config_file: str = 'config.ini', db_path: str = 'user_images.db'):
        """
        初始化数据库连接
        
        Args:
            config_file: 配置文件路径
            db_path: 数据库文件路径
        """
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self.db_path = db_path
        self.max_images_per_user = self.config.getint('user_images', 'max_images_per_user', fallback=10)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建用户图片表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    image_name TEXT NOT NULL,
                    oss_key TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT NOT NULL,
                    upload_time TIMESTAMP NOT NULL,
                    last_accessed TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_images_user_id 
                ON user_images(user_id, upload_time DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_images_oss_key 
                ON user_images(oss_key)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_images_active 
                ON user_images(user_id, is_active, upload_time DESC)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ 用户图片数据库初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    def add_user_image(self, user_image: UserImage) -> bool:
        """
        添加用户图片记录
        
        Args:
            user_image: 用户图片对象
            
        Returns:
            bool: 添加是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户是否已有图片，如果超过限制则删除最旧的
            self._cleanup_old_images(cursor, user_image.user_id)
            
            # 插入新图片记录
            cursor.execute('''
                INSERT INTO user_images 
                (user_id, image_name, oss_key, file_size, mime_type, upload_time, last_accessed, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_image.user_id,
                user_image.image_name,
                user_image.oss_key,
                user_image.file_size,
                user_image.mime_type,
                user_image.upload_time,
                user_image.last_accessed,
                user_image.is_active
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ 用户 {user_image.user_id} 的图片 {user_image.image_name} 添加成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加用户图片失败: {e}")
            return False
    
    def _cleanup_old_images(self, cursor, user_id: str):
        """
        清理用户多余的图片记录（保留最新的N张）
        
        Args:
            cursor: 数据库游标
            user_id: 用户ID
        """
        try:
            # 获取用户当前活跃图片数量
            cursor.execute('''
                SELECT COUNT(*) FROM user_images 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            current_count = cursor.fetchone()[0]
            
            if current_count >= self.max_images_per_user:
                # 获取需要删除的图片（最旧的）
                excess_count = current_count - self.max_images_per_user + 1
                cursor.execute('''
                    SELECT id, oss_key FROM user_images 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY upload_time ASC
                    LIMIT ?
                ''', (user_id, excess_count))
                
                images_to_delete = cursor.fetchall()
                
                # 标记为不活跃
                for image_id, oss_key in images_to_delete:
                    cursor.execute('''
                        UPDATE user_images 
                        SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (image_id,))
                    
                    logger.info(f"标记图片 {oss_key} 为待删除")
                
                logger.info(f"用户 {user_id} 标记了 {len(images_to_delete)} 张图片为待删除")
                
        except Exception as e:
            logger.error(f"❌ 清理旧图片记录失败: {e}")
            raise
    
    def get_user_images(self, user_id: str, active_only: bool = True) -> List[UserImage]:
        """
        获取用户的图片列表
        
        Args:
            user_id: 用户ID
            active_only: 是否只返回活跃图片
            
        Returns:
            List[UserImage]: 图片列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute('''
                    SELECT id, user_id, image_name, oss_key, file_size, mime_type, 
                           upload_time, last_accessed, is_active
                    FROM user_images 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY upload_time DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, user_id, image_name, oss_key, file_size, mime_type, 
                           upload_time, last_accessed, is_active
                    FROM user_images 
                    WHERE user_id = ?
                    ORDER BY upload_time DESC
                ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            images = []
            for row in rows:
                image = UserImage(
                    id=row[0],
                    user_id=row[1],
                    image_name=row[2],
                    oss_key=row[3],
                    file_size=row[4],
                    mime_type=row[5],
                    upload_time=datetime.fromisoformat(row[6]),
                    last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                    is_active=bool(row[8])
                )
                images.append(image)
            
            return images
            
        except Exception as e:
            logger.error(f"❌ 获取用户图片失败: {e}")
            return []
    
    def get_images_to_delete(self, days_old: int = 1) -> List[Tuple[int, str]]:
        """
        获取需要删除的图片记录（标记为不活跃且超过指定天数）
        
        Args:
            days_old: 标记为不活跃多少天后可以删除
            
        Returns:
            List[Tuple[int, str]]: (图片ID, OSS键名) 列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('''
                SELECT id, oss_key FROM user_images 
                WHERE is_active = 0 AND updated_at < ?
                ORDER BY updated_at ASC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return rows
            
        except Exception as e:
            logger.error(f"❌ 获取待删除图片失败: {e}")
            return []
    
    def delete_image_record(self, image_id: int) -> bool:
        """
        删除图片记录
        
        Args:
            image_id: 图片ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM user_images WHERE id = ?', (image_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ 图片记录 {image_id} 删除成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除图片记录失败: {e}")
            return False
    
    def update_image_access_time(self, image_id: int) -> bool:
        """
        更新图片最后访问时间
        
        Args:
            image_id: 图片ID
            
        Returns:
            bool: 更新是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_images 
                SET last_accessed = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (image_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新图片访问时间失败: {e}")
            return False
    
    def get_user_image_stats(self, user_id: str = None) -> Dict[str, Any]:
        """
        获取用户图片统计信息
        
        Args:
            user_id: 用户ID，如果为None则返回所有用户的统计
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                # 单个用户统计
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_images,
                        COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_images,
                        SUM(CASE WHEN is_active = 1 THEN file_size ELSE 0 END) as total_size,
                        MIN(upload_time) as first_upload,
                        MAX(upload_time) as last_upload
                    FROM user_images 
                    WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                stats = {
                    'user_id': user_id,
                    'total_images': result[0],
                    'active_images': result[1],
                    'total_size_bytes': result[2] or 0,
                    'total_size_mb': (result[2] or 0) / (1024 * 1024),
                    'first_upload': result[3],
                    'last_upload': result[4]
                }
            else:
                # 所有用户统计
                cursor.execute('''
                    SELECT 
                        COUNT(DISTINCT user_id) as total_users,
                        COUNT(*) as total_images,
                        COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_images,
                        SUM(CASE WHEN is_active = 1 THEN file_size ELSE 0 END) as total_size,
                        AVG(CASE WHEN is_active = 1 THEN file_size ELSE 0 END) as avg_size
                    FROM user_images
                ''')
                
                result = cursor.fetchone()
                stats = {
                    'total_users': result[0],
                    'total_images': result[1],
                    'active_images': result[2],
                    'total_size_bytes': result[3] or 0,
                    'total_size_mb': (result[3] or 0) / (1024 * 1024),
                    'avg_size_bytes': result[4] or 0,
                    'avg_size_mb': (result[4] or 0) / (1024 * 1024)
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取图片统计失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        logger.info("✅ 用户图片数据库连接已关闭")