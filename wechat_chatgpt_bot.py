#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信群ChatGPT-4机器人
支持微信群消息自动回复，集成ChatGPT-4 API
"""

import os
import json
import time
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
import itchat
from itchat.content import TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT
import openai
from configparser import ConfigParser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeChatChatGPTBot:
    """微信群ChatGPT-4机器人"""
    
    def __init__(self, config_file: str = 'bot_config.ini'):
        """初始化机器人"""
        self.config = self._load_config(config_file)
        self.openai_client = None
        self.chat_history = {}  # 存储聊天历史
        self.max_history = 10   # 最大历史记录数
        self._setup_openai()
        
    def _load_config(self, config_file: str) -> ConfigParser:
        """加载配置文件"""
        config = ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        else:
            # 创建默认配置
            self._create_default_config(config_file)
            config.read(config_file, encoding='utf-8')
        return config
    
    def _create_default_config(self, config_file: str):
        """创建默认配置文件"""
        config = ConfigParser()
        config['OPENAI'] = {
            'api_key': 'your_openai_api_key_here',
            'model': 'gpt-4',
            'max_tokens': '1000',
            'temperature': '0.7'
        }
        config['WECHAT'] = {
            'auto_reply': 'true',
            'reply_groups': 'true',
            'reply_private': 'true',
            'admin_users': 'your_wechat_id'
        }
        config['BOT'] = {
            'name': 'ChatGPT助手',
            'welcome_message': '你好！我是ChatGPT助手，有什么可以帮助你的吗？',
            'error_message': '抱歉，我现在无法回复，请稍后再试。'
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        logger.info(f"已创建默认配置文件: {config_file}")
    
    def _setup_openai(self):
        """设置OpenAI客户端"""
        api_key = self.config.get('OPENAI', 'api_key')
        if api_key and api_key != 'your_openai_api_key_here':
            openai.api_key = api_key
            self.openai_client = openai
            logger.info("OpenAI客户端初始化成功")
        else:
            logger.warning("OpenAI API密钥未配置，请检查配置文件")
    
    async def _call_chatgpt(self, message: str, user_id: str) -> str:
        """调用ChatGPT-4 API"""
        if not self.openai_client:
            return self.config.get('BOT', 'error_message')
        
        try:
            # 获取用户聊天历史
            history = self.chat_history.get(user_id, [])
            
            # 构建消息列表
            messages = []
            
            # 添加系统提示
            messages.append({
                "role": "system", 
                "content": f"你是{self.config.get('BOT', 'name')}，一个友好的AI助手。请用中文回复用户的问题。"
            })
            
            # 添加历史对话
            for msg in history[-self.max_history:]:
                messages.append(msg)
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})
            
            # 调用OpenAI API
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=self.config.get('OPENAI', 'model'),
                messages=messages,
                max_tokens=int(self.config.get('OPENAI', 'max_tokens')),
                temperature=float(self.config.get('OPENAI', 'temperature'))
            )
            
            reply = response.choices[0].message.content.strip()
            
            # 更新聊天历史
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply})
            
            # 保持历史记录在限制范围内
            if len(history) > self.max_history * 2:
                history = history[-(self.max_history * 2):]
            
            self.chat_history[user_id] = history
            
            return reply
            
        except Exception as e:
            logger.error(f"调用ChatGPT API失败: {e}")
            return self.config.get('BOT', 'error_message')
    
    def _should_reply(self, msg) -> bool:
        """判断是否应该回复消息"""
        # 检查是否启用自动回复
        if not self.config.getboolean('WECHAT', 'auto_reply'):
            return False
        
        # 检查消息类型
        if msg['Type'] not in [TEXT, PICTURE, VOICE]:
            return False
        
        # 检查是否在群聊中
        if msg.get('isAt'):
            return self.config.getboolean('WECHAT', 'reply_groups')
        
        # 检查是否是私聊
        if msg['FromUserName'] != msg['ToUserName']:
            return self.config.getboolean('WECHAT', 'reply_private')
        
        return False
    
    def _get_user_id(self, msg) -> str:
        """获取用户ID"""
        if msg.get('isAt'):
            return f"group_{msg['FromUserName']}_{msg['ActualUserName']}"
        else:
            return msg['FromUserName']
    
    @itchat.msg_register([TEXT, PICTURE, VOICE, VIDEO, ATTACHMENT])
    def handle_message(self, msg):
        """处理接收到的消息"""
        try:
            logger.info(f"收到消息: {msg['Content']} 来自: {msg['FromUserName']}")
            
            if not self._should_reply(msg):
                return
            
            user_id = self._get_user_id(msg)
            message_content = msg['Content']
            
            # 处理@消息
            if msg.get('isAt'):
                # 移除@机器人的部分
                message_content = message_content.replace(f"@{self.config.get('BOT', 'name')}", "").strip()
            
            if not message_content:
                return
            
            # 异步调用ChatGPT
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            reply = loop.run_until_complete(self._call_chatgpt(message_content, user_id))
            loop.close()
            
            # 发送回复
            if reply:
                msg['Text'](reply)
                logger.info(f"已回复: {reply}")
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            try:
                msg['Text'](self.config.get('BOT', 'error_message'))
            except:
                pass
    
    def start(self):
        """启动机器人"""
        try:
            logger.info("正在启动微信群ChatGPT机器人...")
            
            # 登录微信
            itchat.auto_login(hotReload=True, loginCallback=self._login_callback)
            
            # 发送欢迎消息
            self._send_welcome_message()
            
            # 开始运行
            itchat.run()
            
        except Exception as e:
            logger.error(f"启动机器人失败: {e}")
    
    def _login_callback(self):
        """登录成功回调"""
        logger.info("微信登录成功！")
        logger.info(f"机器人名称: {self.config.get('BOT', 'name')}")
    
    def _send_welcome_message(self):
        """发送欢迎消息"""
        try:
            # 获取文件传输助手
            file_helper = itchat.search_friends(name='filehelper')
            if file_helper:
                welcome_msg = f"🤖 {self.config.get('BOT', 'name')} 已启动！\n{self.config.get('BOT', 'welcome_message')}"
                itchat.send(welcome_msg, toUserName=file_helper[0]['UserName'])
                logger.info("已发送启动通知")
        except Exception as e:
            logger.error(f"发送欢迎消息失败: {e}")

def main():
    """主函数"""
    print("🤖 微信群ChatGPT-4机器人")
    print("=" * 50)
    
    # 检查配置文件
    if not os.path.exists('bot_config.ini'):
        print("⚠️  首次运行，已创建配置文件 bot_config.ini")
        print("📝 请编辑配置文件，填入您的OpenAI API密钥")
        print("🔑 获取API密钥: https://platform.openai.com/api-keys")
        return
    
    # 创建并启动机器人
    bot = WeChatChatGPTBot()
    bot.start()

if __name__ == "__main__":
    main()