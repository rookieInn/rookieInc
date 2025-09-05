#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面埋点数据模型和MongoDB连接类
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
import json
import uuid
from dataclasses import dataclass, asdict
from configparser import ConfigParser
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserEvent:
    """用户行为事件数据模型"""
    event_id: str
    user_id: Optional[str]
    session_id: str
    event_type: str  # page_view, click, scroll, form_submit, custom等
    page_url: str
    page_title: str
    element_id: Optional[str]  # 被点击的元素ID
    element_class: Optional[str]  # 被点击的元素class
    element_text: Optional[str]  # 被点击的元素文本
    x_position: Optional[int]  # 鼠标X坐标
    y_position: Optional[int]  # 鼠标Y坐标
    scroll_depth: Optional[float]  # 滚动深度百分比
    referrer: Optional[str]  # 来源页面
    user_agent: str
    screen_resolution: Optional[str]  # 屏幕分辨率
    viewport_size: Optional[str]  # 视口大小
    timestamp: datetime
    custom_data: Optional[Dict[str, Any]]  # 自定义数据
    duration: Optional[float]  # 事件持续时间（秒）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 确保datetime对象被正确序列化
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class PageView:
    """页面访问数据模型"""
    page_id: str
    user_id: Optional[str]
    session_id: str
    page_url: str
    page_title: str
    referrer: Optional[str]
    user_agent: str
    screen_resolution: Optional[str]
    viewport_size: Optional[str]
    load_time: Optional[float]  # 页面加载时间
    timestamp: datetime
    exit_timestamp: Optional[datetime]  # 离开页面时间
    duration: Optional[float]  # 页面停留时间

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.exit_timestamp:
            data['exit_timestamp'] = self.exit_timestamp.isoformat()
        return data

class TrackingDatabase:
    """埋点数据MongoDB连接和操作类"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """
        初始化数据库连接
        
        Args:
            config_file: 配置文件路径
        """
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # MongoDB连接配置
        mongo_host = self.config.get('mongodb', 'host', fallback='localhost')
        mongo_port = self.config.getint('mongodb', 'port', fallback=27017)
        mongo_username = self.config.get('mongodb', 'username', fallback='')
        mongo_password = self.config.get('mongodb', 'password', fallback='')
        mongo_database = self.config.get('mongodb', 'database', fallback='tracking')
        
        # 构建连接字符串
        if mongo_username and mongo_password:
            connection_string = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}"
        else:
            connection_string = f"mongodb://{mongo_host}:{mongo_port}/{mongo_database}"
        
        try:
            self.client = MongoClient(connection_string)
            self.db: Database = self.client[mongo_database]
            
            # 获取集合
            self.events_collection: Collection = self.db['user_events']
            self.pageviews_collection: Collection = self.db['page_views']
            self.sessions_collection: Collection = self.db['user_sessions']
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"✅ MongoDB连接成功: {mongo_database}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引以提高查询性能"""
        try:
            # 用户事件索引
            self.events_collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            self.events_collection.create_index([("session_id", ASCENDING), ("timestamp", DESCENDING)])
            self.events_collection.create_index([("event_type", ASCENDING), ("timestamp", DESCENDING)])
            self.events_collection.create_index([("page_url", ASCENDING), ("timestamp", DESCENDING)])
            self.events_collection.create_index("timestamp")
            
            # 页面访问索引
            self.pageviews_collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            self.pageviews_collection.create_index([("session_id", ASCENDING), ("timestamp", DESCENDING)])
            self.pageviews_collection.create_index([("page_url", ASCENDING), ("timestamp", DESCENDING)])
            self.pageviews_collection.create_index("timestamp")
            
            # 会话索引
            self.sessions_collection.create_index([("user_id", ASCENDING), ("start_time", DESCENDING)])
            self.sessions_collection.create_index("session_id", unique=True)
            self.sessions_collection.create_index("start_time")
            
            logger.info("✅ 数据库索引创建成功")
            
        except Exception as e:
            logger.warning(f"⚠️ 索引创建失败: {e}")
    
    def insert_event(self, event: UserEvent) -> bool:
        """
        插入用户事件数据
        
        Args:
            event: 用户事件对象
            
        Returns:
            bool: 插入是否成功
        """
        try:
            result = self.events_collection.insert_one(event.to_dict())
            logger.info(f"✅ 事件插入成功: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 事件插入失败: {e}")
            return False
    
    def insert_pageview(self, pageview: PageView) -> bool:
        """
        插入页面访问数据
        
        Args:
            pageview: 页面访问对象
            
        Returns:
            bool: 插入是否成功
        """
        try:
            result = self.pageviews_collection.insert_one(pageview.to_dict())
            logger.info(f"✅ 页面访问数据插入成功: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 页面访问数据插入失败: {e}")
            return False
    
    def get_events_by_user(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        获取指定用户的事件数据
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 事件数据列表
        """
        try:
            cursor = self.events_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ 获取用户事件失败: {e}")
            return []
    
    def get_events_by_session(self, session_id: str) -> List[Dict]:
        """
        获取指定会话的事件数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            List[Dict]: 事件数据列表
        """
        try:
            cursor = self.events_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", ASCENDING)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ 获取会话事件失败: {e}")
            return []
    
    def get_page_views_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        获取指定日期范围的页面访问数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 页面访问数据列表
        """
        try:
            cursor = self.pageviews_collection.find({
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).sort("timestamp", DESCENDING)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ 获取页面访问数据失败: {e}")
            return []
    
    def get_event_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        获取事件统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1},
                        "unique_users": {"$addToSet": "$user_id"}
                    }
                },
                {
                    "$project": {
                        "event_type": "$_id",
                        "count": 1,
                        "unique_users_count": {"$size": "$unique_users"}
                    }
                }
            ]
            
            result = list(self.events_collection.aggregate(pipeline))
            
            # 计算总事件数
            total_events = sum(item['count'] for item in result)
            
            return {
                "total_events": total_events,
                "event_types": result,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 获取事件统计失败: {e}")
            return {}
    
    def get_page_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        获取页面统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[str, Any]: 页面统计信息
        """
        try:
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$page_url",
                        "page_title": {"$first": "$page_title"},
                        "views": {"$sum": 1},
                        "unique_users": {"$addToSet": "$user_id"},
                        "avg_duration": {"$avg": "$duration"}
                    }
                },
                {
                    "$project": {
                        "page_url": "$_id",
                        "page_title": 1,
                        "views": 1,
                        "unique_users_count": {"$size": "$unique_users"},
                        "avg_duration": {"$round": ["$avg_duration", 2]}
                    }
                },
                {
                    "$sort": {"views": -1}
                }
            ]
            
            result = list(self.pageviews_collection.aggregate(pipeline))
            
            return {
                "total_pages": len(result),
                "pages": result,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 获取页面统计失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("✅ MongoDB连接已关闭")

def generate_session_id() -> str:
    """生成会话ID"""
    return str(uuid.uuid4())

def generate_event_id() -> str:
    """生成事件ID"""
    return str(uuid.uuid4())