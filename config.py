"""
系统配置文件
"""

import os
from datetime import timedelta

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///livestream_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 门禁配置
    DOOR_UNLOCK_DURATION = int(os.environ.get('DOOR_UNLOCK_DURATION', '30'))  # 门禁解锁持续时间（秒）
    AUTO_LOCK_DELAY = int(os.environ.get('AUTO_LOCK_DELAY', '300'))  # 预约结束后自动锁门延迟（秒）
    CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '30'))  # 定时检查间隔（秒）
    
    # 预约配置
    MAX_BOOKING_DURATION = int(os.environ.get('MAX_BOOKING_DURATION', '480'))  # 最大预约时长（分钟）
    MIN_BOOKING_DURATION = int(os.environ.get('MIN_BOOKING_DURATION', '30'))   # 最小预约时长（分钟）
    ADVANCE_BOOKING_DAYS = int(os.environ.get('ADVANCE_BOOKING_DAYS', '7'))    # 可提前预约天数
    
    # 硬件配置
    HARDWARE_SIMULATION = os.environ.get('HARDWARE_SIMULATION', 'True').lower() == 'true'
    HARDWARE_PORT = int(os.environ.get('HARDWARE_PORT', '8080'))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'livestream_management.log')
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 会话超时时间（秒）
    
    # 通知配置
    ENABLE_NOTIFICATIONS = os.environ.get('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')
    NOTIFICATION_PHONE = os.environ.get('NOTIFICATION_PHONE', '')
    
    # 房间配置
    DEFAULT_ROOMS = [
        {'name': '直播间1', 'capacity': 4},
        {'name': '直播间2', 'capacity': 6},
        {'name': '直播间3', 'capacity': 8},
    ]
    
    # 时间配置
    WORKING_HOURS = {
        'start': '08:00',
        'end': '22:00'
    }
    
    # 节假日配置（示例）
    HOLIDAYS = [
        '2024-01-01',  # 元旦
        '2024-02-10',  # 春节
        '2024-02-11',
        '2024-02-12',
        '2024-04-05',  # 清明节
        '2024-05-01',  # 劳动节
        '2024-06-10',  # 端午节
        '2024-09-17',  # 中秋节
        '2024-10-01',  # 国庆节
        '2024-10-02',
        '2024-10-03',
    ]

class DevelopmentConfig(Config):
    DEBUG = True
    HARDWARE_SIMULATION = True

class ProductionConfig(Config):
    DEBUG = False
    HARDWARE_SIMULATION = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}