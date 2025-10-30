#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号自定义菜单管理
支持多级菜单、点击返回图片/视频/音频
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Any
from configparser import ConfigParser
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_official_menu.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeChatOfficialMenuManager:
    """微信公众号菜单管理器"""
    
    # API地址
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    TOKEN_URL = f"{API_BASE}/token"
    MENU_CREATE_URL = f"{API_BASE}/menu/create"
    MENU_GET_URL = f"{API_BASE}/menu/get"
    MENU_DELETE_URL = f"{API_BASE}/menu/delete"
    MEDIA_UPLOAD_URL = f"{API_BASE}/material/add_material"
    MEDIA_UPLOAD_NEWS_URL = f"{API_BASE}/material/add_news"
    
    def __init__(self, config_file: str = 'wechat_official_account_config.ini'):
        """初始化菜单管理器"""
        self.config = self._load_config(config_file)
        self.appid = self.config.get('WECHAT_OFFICIAL', 'appid')
        self.appsecret = self.config.get('WECHAT_OFFICIAL', 'appsecret')
        self.access_token = None
        self.token_expires_at = 0
        
        # 创建媒体文件目录
        self._create_media_directories()
    
    def _load_config(self, config_file: str) -> ConfigParser:
        """加载配置文件"""
        config = ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        config.read(config_file, encoding='utf-8')
        return config
    
    def _create_media_directories(self):
        """创建媒体文件目录"""
        for media_type in ['image_path', 'video_path', 'audio_path']:
            path = self.config.get('MEDIA', media_type)
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.info(f"媒体目录已创建: {path}")
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取access_token
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            access_token字符串
        """
        # 检查token是否过期
        if not force_refresh and self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        try:
            params = {
                'grant_type': 'client_credential',
                'appid': self.appid,
                'secret': self.appsecret
            }
            
            response = requests.get(self.TOKEN_URL, params=params, timeout=10)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # 提前5分钟过期，避免边界情况
                self.token_expires_at = time.time() + result.get('expires_in', 7200) - 300
                logger.info("access_token获取成功")
                return self.access_token
            else:
                error_msg = f"获取access_token失败: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            raise
    
    def upload_media(self, file_path: str, media_type: str = 'image') -> Optional[str]:
        """
        上传永久素材
        
        Args:
            file_path: 文件路径
            media_type: 媒体类型 (image/voice/video/thumb)
            
        Returns:
            media_id
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None
        
        try:
            access_token = self.get_access_token()
            url = f"{self.MEDIA_UPLOAD_URL}?access_token={access_token}&type={media_type}"
            
            with open(file_path, 'rb') as f:
                files = {'media': f}
                
                # 视频需要额外的描述信息
                if media_type == 'video':
                    data = {
                        'description': json.dumps({
                            'title': os.path.basename(file_path),
                            'introduction': '视频描述'
                        })
                    }
                    response = requests.post(url, files=files, data=data, timeout=30)
                else:
                    response = requests.post(url, files=files, timeout=30)
                
                result = response.json()
                
                if 'media_id' in result:
                    logger.info(f"素材上传成功: {file_path} -> {result['media_id']}")
                    return result['media_id']
                else:
                    logger.error(f"素材上传失败: {result}")
                    return None
                    
        except Exception as e:
            logger.error(f"上传素材异常: {e}")
            return None
    
    def create_menu(self, menu_data: Dict) -> bool:
        """
        创建自定义菜单
        
        Args:
            menu_data: 菜单数据字典
            
        Returns:
            是否成功
        """
        try:
            access_token = self.get_access_token()
            url = f"{self.MENU_CREATE_URL}?access_token={access_token}"
            
            response = requests.post(
                url,
                json=menu_data,
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=10
            )
            
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info("菜单创建成功")
                return True
            else:
                logger.error(f"菜单创建失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"创建菜单异常: {e}")
            return False
    
    def get_menu(self) -> Optional[Dict]:
        """
        查询当前菜单
        
        Returns:
            菜单数据字典
        """
        try:
            access_token = self.get_access_token()
            url = f"{self.MENU_GET_URL}?access_token={access_token}"
            
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if 'menu' in result:
                logger.info("菜单查询成功")
                return result
            else:
                logger.error(f"菜单查询失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"查询菜单异常: {e}")
            return None
    
    def delete_menu(self) -> bool:
        """
        删除当前菜单
        
        Returns:
            是否成功
        """
        try:
            access_token = self.get_access_token()
            url = f"{self.MENU_DELETE_URL}?access_token={access_token}"
            
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info("菜单删除成功")
                return True
            else:
                logger.error(f"菜单删除失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"删除菜单异常: {e}")
            return False
    
    def create_example_menu(self) -> bool:
        """
        创建示例菜单
        包含多级菜单和不同类型的响应
        
        Returns:
            是否成功
        """
        menu_data = {
            "button": [
                {
                    "name": "📱 功能区",
                    "sub_button": [
                        {
                            "type": "click",
                            "name": "📸 查看图片",
                            "key": "MENU_IMAGE_1"
                        },
                        {
                            "type": "click",
                            "name": "🎬 观看视频",
                            "key": "MENU_VIDEO_1"
                        },
                        {
                            "type": "click",
                            "name": "🎵 听音频",
                            "key": "MENU_AUDIO_1"
                        },
                        {
                            "type": "view",
                            "name": "🌐 访问网站",
                            "url": "https://www.example.com"
                        }
                    ]
                },
                {
                    "name": "ℹ️ 信息中心",
                    "sub_button": [
                        {
                            "type": "click",
                            "name": "📰 最新资讯",
                            "key": "MENU_NEWS"
                        },
                        {
                            "type": "click",
                            "name": "🎁 精美图片",
                            "key": "MENU_IMAGE_2"
                        },
                        {
                            "type": "click",
                            "name": "🔔 通知公告",
                            "key": "MENU_NOTICE"
                        }
                    ]
                },
                {
                    "name": "🛠️ 关于",
                    "sub_button": [
                        {
                            "type": "click",
                            "name": "👤 关于我们",
                            "key": "MENU_ABOUT"
                        },
                        {
                            "type": "click",
                            "name": "📞 联系方式",
                            "key": "MENU_CONTACT"
                        },
                        {
                            "type": "click",
                            "name": "❓ 帮助中心",
                            "key": "MENU_HELP"
                        }
                    ]
                }
            ]
        }
        
        logger.info("正在创建示例菜单...")
        return self.create_menu(menu_data)
    
    def build_custom_menu(
        self,
        buttons: List[Dict[str, Any]]
    ) -> Dict:
        """
        构建自定义菜单数据
        
        Args:
            buttons: 菜单按钮列表
            
        Returns:
            菜单数据字典
            
        示例:
        buttons = [
            {
                "name": "一级菜单1",
                "sub_button": [
                    {"type": "click", "name": "子菜单1", "key": "KEY1"},
                    {"type": "view", "name": "子菜单2", "url": "http://example.com"}
                ]
            },
            {
                "type": "click",
                "name": "一级菜单2",
                "key": "KEY2"
            }
        ]
        """
        if len(buttons) > 3:
            logger.warning("一级菜单最多3个，将只使用前3个")
            buttons = buttons[:3]
        
        for button in buttons:
            if 'sub_button' in button and len(button['sub_button']) > 5:
                logger.warning(f"子菜单 '{button['name']}' 最多5个，将只使用前5个")
                button['sub_button'] = button['sub_button'][:5]
        
        return {"button": buttons}


def main():
    """主函数 - 示例用法"""
    print("🎯 微信公众号自定义菜单管理")
    print("=" * 60)
    
    try:
        # 初始化管理器
        manager = WeChatOfficialMenuManager()
        
        # 获取access_token
        print("\n📝 正在获取access_token...")
        token = manager.get_access_token()
        print(f"✅ access_token: {token[:20]}...")
        
        # 查询当前菜单
        print("\n🔍 查询当前菜单...")
        current_menu = manager.get_menu()
        if current_menu:
            print("✅ 当前菜单:")
            print(json.dumps(current_menu, ensure_ascii=False, indent=2))
        
        # 创建示例菜单
        print("\n🎨 是否创建示例菜单? (y/n): ", end='')
        choice = input().strip().lower()
        
        if choice == 'y':
            print("\n📋 正在创建示例菜单...")
            if manager.create_example_menu():
                print("✅ 示例菜单创建成功！")
                print("\n💡 提示:")
                print("   1. 请关注您的公众号查看菜单")
                print("   2. 菜单生效可能需要24小时")
                print("   3. 重新关注公众号可立即看到新菜单")
            else:
                print("❌ 菜单创建失败，请检查日志")
        else:
            print("⏭️  跳过菜单创建")
        
        print("\n" + "=" * 60)
        print("✨ 完成！")
        
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("💡 请先配置 wechat_official_account_config.ini 文件")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        logger.error(f"程序执行失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()
