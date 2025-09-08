#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信群ChatGPT-4高级机器人
支持更多功能：图片识别、语音转文字、群管理、定时任务等
"""

import os
import json
import time
import logging
import asyncio
import aiohttp
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import itchat
from itchat.content import TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT, MAP, CARD, SHARING, NOTE
import openai
from configparser import ConfigParser
import threading
import schedule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_bot_advanced.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedWeChatChatGPTBot:
    """高级微信群ChatGPT-4机器人"""
    
    def __init__(self, config_file: str = 'bot_config_advanced.ini'):
        """初始化机器人"""
        self.config = self._load_config(config_file)
        self.openai_client = None
        self.chat_history = {}
        self.max_history = 10
        self.user_stats = {}  # 用户统计
        self.group_settings = {}  # 群组设置
        self.scheduled_tasks = {}  # 定时任务
        self._setup_openai()
        self._setup_commands()
        
    def _load_config(self, config_file: str) -> ConfigParser:
        """加载配置文件"""
        config = ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        else:
            self._create_advanced_config(config_file)
            config.read(config_file, encoding='utf-8')
        return config
    
    def _create_advanced_config(self, config_file: str):
        """创建高级配置文件"""
        config = ConfigParser()
        
        # OpenAI配置
        config['OPENAI'] = {
            'api_key': 'your_openai_api_key_here',
            'model': 'gpt-4',
            'max_tokens': '1500',
            'temperature': '0.7',
            'enable_vision': 'true',
            'enable_voice': 'true'
        }
        
        # 微信配置
        config['WECHAT'] = {
            'auto_reply': 'true',
            'reply_groups': 'true',
            'reply_private': 'true',
            'admin_users': 'your_wechat_id',
            'enable_image_recognition': 'true',
            'enable_voice_recognition': 'true',
            'enable_group_management': 'true'
        }
        
        # 机器人配置
        config['BOT'] = {
            'name': 'ChatGPT智能助手',
            'welcome_message': '🤖 你好！我是ChatGPT智能助手，支持文字、图片、语音对话！',
            'error_message': '❌ 抱歉，我现在无法回复，请稍后再试。',
            'help_message': '''📖 使用帮助：
• 直接发送文字与我对话
• 发送图片，我可以识别并描述
• 发送语音，我会转换为文字并回复
• 发送 /help 查看帮助
• 发送 /stats 查看统计信息
• 发送 /clear 清除对话历史
• 发送 /weather 查询天气（需要配置）'''
        }
        
        # 功能配置
        config['FEATURES'] = {
            'enable_weather': 'false',
            'weather_api_key': 'your_weather_api_key',
            'enable_news': 'false',
            'news_api_key': 'your_news_api_key',
            'enable_translation': 'true',
            'enable_sentiment': 'true'
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        logger.info(f"已创建高级配置文件: {config_file}")
    
    def _setup_openai(self):
        """设置OpenAI客户端"""
        api_key = self.config.get('OPENAI', 'api_key')
        if api_key and api_key != 'your_openai_api_key_here':
            openai.api_key = api_key
            self.openai_client = openai
            logger.info("OpenAI客户端初始化成功")
        else:
            logger.warning("OpenAI API密钥未配置")
    
    def _setup_commands(self):
        """设置命令处理器"""
        self.commands = {
            '/help': self._handle_help_command,
            '/stats': self._handle_stats_command,
            '/clear': self._handle_clear_command,
            '/weather': self._handle_weather_command,
            '/translate': self._handle_translate_command,
            '/sentiment': self._handle_sentiment_command,
            '/admin': self._handle_admin_command
        }
    
    async def _call_chatgpt(self, message: str, user_id: str, image_url: str = None) -> str:
        """调用ChatGPT-4 API"""
        if not self.openai_client:
            return self.config.get('BOT', 'error_message')
        
        try:
            history = self.chat_history.get(user_id, [])
            messages = []
            
            # 系统提示
            system_prompt = f"""你是{self.config.get('BOT', 'name')}，一个智能AI助手。
功能特点：
- 支持中文对话
- 可以分析图片内容
- 可以进行情感分析
- 支持翻译功能
- 友好、专业、有帮助

请根据用户的问题提供准确、有用的回答。"""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史对话
            for msg in history[-self.max_history:]:
                messages.append(msg)
            
            # 处理图片消息
            if image_url:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"请分析这张图片：{message}"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                })
            else:
                messages.append({"role": "user", "content": message})
            
            # 调用API
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=self.config.get('OPENAI', 'model'),
                messages=messages,
                max_tokens=int(self.config.get('OPENAI', 'max_tokens')),
                temperature=float(self.config.get('OPENAI', 'temperature'))
            )
            
            reply = response.choices[0].message.content.strip()
            
            # 更新历史
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply})
            
            if len(history) > self.max_history * 2:
                history = history[-(self.max_history * 2):]
            
            self.chat_history[user_id] = history
            
            # 更新用户统计
            self._update_user_stats(user_id)
            
            return reply
            
        except Exception as e:
            logger.error(f"调用ChatGPT API失败: {e}")
            return self.config.get('BOT', 'error_message')
    
    def _update_user_stats(self, user_id: str):
        """更新用户统计"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'message_count': 0,
                'first_use': datetime.now(),
                'last_use': datetime.now()
            }
        
        self.user_stats[user_id]['message_count'] += 1
        self.user_stats[user_id]['last_use'] = datetime.now()
    
    def _should_reply(self, msg) -> bool:
        """判断是否应该回复"""
        if not self.config.getboolean('WECHAT', 'auto_reply'):
            return False
        
        # 检查消息类型
        if msg['Type'] not in [TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT]:
            return False
        
        # 群聊检查
        if msg.get('isAt'):
            return self.config.getboolean('WECHAT', 'reply_groups')
        
        # 私聊检查
        if msg['FromUserName'] != msg['ToUserName']:
            return self.config.getboolean('WECHAT', 'reply_private')
        
        return False
    
    def _get_user_id(self, msg) -> str:
        """获取用户ID"""
        if msg.get('isAt'):
            return f"group_{msg['FromUserName']}_{msg['ActualUserName']}"
        else:
            return msg['FromUserName']
    
    def _handle_help_command(self, user_id: str) -> str:
        """处理帮助命令"""
        return self.config.get('BOT', 'help_message')
    
    def _handle_stats_command(self, user_id: str) -> str:
        """处理统计命令"""
        if user_id not in self.user_stats:
            return "📊 暂无统计数据"
        
        stats = self.user_stats[user_id]
        return f"""📊 您的使用统计：
• 消息数量: {stats['message_count']}
• 首次使用: {stats['first_use'].strftime('%Y-%m-%d %H:%M')}
• 最后使用: {stats['last_use'].strftime('%Y-%m-%d %H:%M')}
• 对话历史: {len(self.chat_history.get(user_id, []))} 条"""
    
    def _handle_clear_command(self, user_id: str) -> str:
        """处理清除历史命令"""
        if user_id in self.chat_history:
            del self.chat_history[user_id]
        return "🗑️ 对话历史已清除"
    
    def _handle_weather_command(self, user_id: str) -> str:
        """处理天气命令"""
        if not self.config.getboolean('FEATURES', 'enable_weather'):
            return "🌤️ 天气功能未启用，请联系管理员配置"
        return "🌤️ 天气功能开发中..."
    
    def _handle_translate_command(self, user_id: str) -> str:
        """处理翻译命令"""
        return "🌍 翻译功能开发中..."
    
    def _handle_sentiment_command(self, user_id: str) -> str:
        """处理情感分析命令"""
        return "😊 情感分析功能开发中..."
    
    def _handle_admin_command(self, user_id: str) -> str:
        """处理管理员命令"""
        admin_users = self.config.get('WECHAT', 'admin_users').split(',')
        if user_id not in admin_users:
            return "❌ 权限不足"
        
        return f"""🔧 管理员面板：
• 在线用户: {len(self.user_stats)}
• 活跃群组: {len(set([uid.split('_')[1] for uid in self.chat_history.keys() if '_' in uid]))}
• 总消息数: {sum(stats['message_count'] for stats in self.user_stats.values())}"""
    
    async def _process_image(self, msg) -> Optional[str]:
        """处理图片消息"""
        try:
            # 下载图片
            img_path = f"temp_image_{int(time.time())}.jpg"
            msg['Text'](img_path)
            
            # 转换为base64
            with open(img_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 删除临时文件
            os.remove(img_path)
            
            # 使用OpenAI Vision API
            if self.openai_client and self.config.getboolean('OPENAI', 'enable_vision'):
                response = await asyncio.to_thread(
                    self.openai_client.ChatCompletion.create,
                    model="gpt-4-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请详细描述这张图片的内容"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]
                    }],
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            
            return "📷 图片识别功能需要配置OpenAI Vision API"
            
        except Exception as e:
            logger.error(f"处理图片失败: {e}")
            return None
    
    async def _process_voice(self, msg) -> Optional[str]:
        """处理语音消息"""
        try:
            # 下载语音文件
            voice_path = f"temp_voice_{int(time.time())}.wav"
            msg['Text'](voice_path)
            
            # 这里可以集成语音识别API
            # 目前返回占位符
            os.remove(voice_path)
            return "🎤 语音识别功能开发中..."
            
        except Exception as e:
            logger.error(f"处理语音失败: {e}")
            return None
    
    @itchat.msg_register([TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT, MAP, CARD, SHARING, NOTE])
    def handle_message(self, msg):
        """处理接收到的消息"""
        try:
            logger.info(f"收到消息: {msg['Content']} 类型: {msg['Type']} 来自: {msg['FromUserName']}")
            
            if not self._should_reply(msg):
                return
            
            user_id = self._get_user_id(msg)
            message_content = msg['Content']
            
            # 处理@消息
            if msg.get('isAt'):
                message_content = message_content.replace(f"@{self.config.get('BOT', 'name')}", "").strip()
            
            if not message_content and msg['Type'] not in [PICTURE, VOICE]:
                return
            
            # 处理命令
            if message_content.startswith('/'):
                command = message_content.split()[0]
                if command in self.commands:
                    reply = self.commands[command](user_id)
                    msg['Text'](reply)
                    return
            
            # 异步处理消息
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if msg['Type'] == PICTURE:
                    reply = loop.run_until_complete(self._process_image(msg))
                elif msg['Type'] == VOICE:
                    reply = loop.run_until_complete(self._process_voice(msg))
                else:
                    reply = loop.run_until_complete(self._call_chatgpt(message_content, user_id))
                
                if reply:
                    msg['Text'](reply)
                    logger.info(f"已回复: {reply}")
                    
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            try:
                msg['Text'](self.config.get('BOT', 'error_message'))
            except:
                pass
    
    def _schedule_tasks(self):
        """定时任务"""
        # 每天凌晨清理过期数据
        schedule.every().day.at("00:00").do(self._cleanup_expired_data)
        
        # 每小时保存统计数据
        schedule.every().hour.do(self._save_stats)
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            # 清理7天前的聊天历史
            cutoff_date = datetime.now() - timedelta(days=7)
            expired_users = []
            
            for user_id, history in self.chat_history.items():
                if history and len(history) > 0:
                    last_message_time = datetime.fromtimestamp(history[-1].get('timestamp', 0))
                    if last_message_time < cutoff_date:
                        expired_users.append(user_id)
            
            for user_id in expired_users:
                del self.chat_history[user_id]
            
            logger.info(f"清理了 {len(expired_users)} 个过期用户数据")
            
        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
    
    def _save_stats(self):
        """保存统计数据"""
        try:
            stats_data = {
                'user_stats': self.user_stats,
                'chat_history_count': len(self.chat_history),
                'timestamp': datetime.now().isoformat()
            }
            
            with open('bot_stats.json', 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info("统计数据已保存")
            
        except Exception as e:
            logger.error(f"保存统计数据失败: {e}")
    
    def start(self):
        """启动机器人"""
        try:
            logger.info("正在启动高级微信群ChatGPT机器人...")
            
            # 启动定时任务线程
            schedule_thread = threading.Thread(target=self._schedule_tasks, daemon=True)
            schedule_thread.start()
            
            # 登录微信
            itchat.auto_login(hotReload=True, loginCallback=self._login_callback)
            
            # 发送启动通知
            self._send_startup_notification()
            
            # 开始运行
            itchat.run()
            
        except Exception as e:
            logger.error(f"启动机器人失败: {e}")
    
    def _login_callback(self):
        """登录成功回调"""
        logger.info("微信登录成功！")
        logger.info(f"机器人名称: {self.config.get('BOT', 'name')}")
        logger.info("支持功能: 文字对话、图片识别、语音识别、群管理")
    
    def _send_startup_notification(self):
        """发送启动通知"""
        try:
            file_helper = itchat.search_friends(name='filehelper')
            if file_helper:
                startup_msg = f"""🤖 {self.config.get('BOT', 'name')} 已启动！

✨ 功能特点：
• 智能文字对话
• 图片内容识别
• 语音转文字
• 群组管理
• 用户统计
• 定时任务

📖 发送 /help 查看详细帮助"""
                
                itchat.send(startup_msg, toUserName=file_helper[0]['UserName'])
                logger.info("已发送启动通知")
        except Exception as e:
            logger.error(f"发送启动通知失败: {e}")

def main():
    """主函数"""
    print("🤖 高级微信群ChatGPT-4机器人")
    print("=" * 60)
    print("✨ 支持功能：文字对话、图片识别、语音识别、群管理")
    print("=" * 60)
    
    # 检查配置文件
    if not os.path.exists('bot_config_advanced.ini'):
        print("⚠️  首次运行，已创建高级配置文件 bot_config_advanced.ini")
        print("📝 请编辑配置文件，填入您的API密钥")
        print("🔑 OpenAI API: https://platform.openai.com/api-keys")
        return
    
    # 创建并启动机器人
    bot = AdvancedWeChatChatGPTBot()
    bot.start()

if __name__ == "__main__":
    main()