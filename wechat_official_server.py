#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号消息响应服务器
处理菜单点击事件，返回图片、视频、音频等媒体内容
"""

import os
import time
import hashlib
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from configparser import ConfigParser
from flask import Flask, request, make_response
from wechat_official_menu import WeChatOfficialMenuManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_official_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 全局配置
config = None
menu_manager = None
media_cache = {}  # 缓存媒体文件的media_id


def load_config(config_file: str = 'wechat_official_account_config.ini') -> ConfigParser:
    """加载配置文件"""
    cfg = ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    cfg.read(config_file, encoding='utf-8')
    return cfg


def verify_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """
    验证微信服务器签名
    
    Args:
        signature: 微信加密签名
        timestamp: 时间戳
        nonce: 随机数
        
    Returns:
        是否验证通过
    """
    token = config.get('WECHAT_OFFICIAL', 'token')
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    tmp_signature = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return tmp_signature == signature


def parse_xml_message(xml_data: str) -> Dict:
    """
    解析XML消息
    
    Args:
        xml_data: XML数据
        
    Returns:
        消息字典
    """
    try:
        root = ET.fromstring(xml_data)
        msg = {}
        for child in root:
            msg[child.tag] = child.text
        return msg
    except Exception as e:
        logger.error(f"解析XML失败: {e}")
        return {}


def build_text_response(to_user: str, from_user: str, content: str) -> str:
    """
    构建文本消息响应
    
    Args:
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        content: 文本内容
        
    Returns:
        XML格式的响应
    """
    template = """<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
</xml>"""
    
    return template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        content=content
    )


def build_image_response(to_user: str, from_user: str, media_id: str) -> str:
    """
    构建图片消息响应
    
    Args:
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        media_id: 图片素材ID
        
    Returns:
        XML格式的响应
    """
    template = """<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
        <MediaId><![CDATA[{media_id}]]></MediaId>
    </Image>
</xml>"""
    
    return template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        media_id=media_id
    )


def build_video_response(
    to_user: str,
    from_user: str,
    media_id: str,
    title: str = "",
    description: str = ""
) -> str:
    """
    构建视频消息响应
    
    Args:
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        media_id: 视频素材ID
        title: 视频标题
        description: 视频描述
        
    Returns:
        XML格式的响应
    """
    template = """<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[video]]></MsgType>
    <Video>
        <MediaId><![CDATA[{media_id}]]></MediaId>
        <Title><![CDATA[{title}]]></Title>
        <Description><![CDATA[{description}]]></Description>
    </Video>
</xml>"""
    
    return template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        media_id=media_id,
        title=title,
        description=description
    )


def build_voice_response(to_user: str, from_user: str, media_id: str) -> str:
    """
    构建语音消息响应
    
    Args:
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        media_id: 语音素材ID
        
    Returns:
        XML格式的响应
    """
    template = """<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[voice]]></MsgType>
    <Voice>
        <MediaId><![CDATA[{media_id}]]></MediaId>
    </Voice>
</xml>"""
    
    return template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        media_id=media_id
    )


def build_news_response(
    to_user: str,
    from_user: str,
    articles: list
) -> str:
    """
    构建图文消息响应
    
    Args:
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        articles: 图文列表，每个元素包含 title, description, pic_url, url
        
    Returns:
        XML格式的响应
    """
    article_items = ""
    for article in articles[:8]:  # 最多8条图文
        article_items += f"""
        <item>
            <Title><![CDATA[{article.get('title', '')}]]></Title>
            <Description><![CDATA[{article.get('description', '')}]]></Description>
            <PicUrl><![CDATA[{article.get('pic_url', '')}]]></PicUrl>
            <Url><![CDATA[{article.get('url', '')}]]></Url>
        </item>"""
    
    template = """<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>{count}</ArticleCount>
    <Articles>{articles}</Articles>
</xml>"""
    
    return template.format(
        to_user=to_user,
        from_user=from_user,
        create_time=int(time.time()),
        count=len(articles),
        articles=article_items
    )


def handle_menu_click(event_key: str, to_user: str, from_user: str) -> str:
    """
    处理菜单点击事件
    
    Args:
        event_key: 菜单KEY
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        
    Returns:
        响应消息XML
    """
    logger.info(f"菜单点击: {event_key}")
    
    # 图片响应示例
    if event_key == "MENU_IMAGE_1":
        # 检查缓存
        if event_key in media_cache:
            media_id = media_cache[event_key]
        else:
            # 上传图片获取media_id
            image_path = os.path.join(
                config.get('MEDIA', 'image_path'),
                'sample_image_1.jpg'
            )
            if os.path.exists(image_path):
                media_id = menu_manager.upload_media(image_path, 'image')
                if media_id:
                    media_cache[event_key] = media_id
                else:
                    return build_text_response(to_user, from_user, "图片加载失败，请稍后再试")
            else:
                return build_text_response(
                    to_user,
                    from_user,
                    f"📸 这是一张精美的图片！\n\n💡 请将图片放置在: {image_path}"
                )
        
        return build_image_response(to_user, from_user, media_id)
    
    # 另一个图片响应
    elif event_key == "MENU_IMAGE_2":
        return build_text_response(
            to_user,
            from_user,
            "🎨 这里是精美图片展示区！\n\n您可以看到各种精美的图片内容。"
        )
    
    # 视频响应示例
    elif event_key == "MENU_VIDEO_1":
        if event_key in media_cache:
            media_id = media_cache[event_key]
        else:
            video_path = os.path.join(
                config.get('MEDIA', 'video_path'),
                'sample_video_1.mp4'
            )
            if os.path.exists(video_path):
                media_id = menu_manager.upload_media(video_path, 'video')
                if media_id:
                    media_cache[event_key] = media_id
                else:
                    return build_text_response(to_user, from_user, "视频加载失败，请稍后再试")
            else:
                return build_text_response(
                    to_user,
                    from_user,
                    f"🎬 这是一个精彩视频！\n\n💡 请将视频放置在: {video_path}"
                )
        
        return build_video_response(
            to_user,
            from_user,
            media_id,
            title="精彩视频",
            description="欢迎观看我们的视频内容"
        )
    
    # 音频响应示例
    elif event_key == "MENU_AUDIO_1":
        if event_key in media_cache:
            media_id = media_cache[event_key]
        else:
            audio_path = os.path.join(
                config.get('MEDIA', 'audio_path'),
                'sample_audio_1.mp3'
            )
            if os.path.exists(audio_path):
                media_id = menu_manager.upload_media(audio_path, 'voice')
                if media_id:
                    media_cache[event_key] = media_id
                else:
                    return build_text_response(to_user, from_user, "音频加载失败，请稍后再试")
            else:
                return build_text_response(
                    to_user,
                    from_user,
                    f"🎵 这是一段美妙的音频！\n\n💡 请将音频放置在: {audio_path}"
                )
        
        return build_voice_response(to_user, from_user, media_id)
    
    # 图文消息示例
    elif event_key == "MENU_NEWS":
        articles = [
            {
                "title": "📰 最新资讯 - 标题1",
                "description": "这是资讯的详细描述内容",
                "pic_url": "https://via.placeholder.com/300x200",
                "url": "https://www.example.com/news/1"
            },
            {
                "title": "📰 最新资讯 - 标题2",
                "description": "这是另一条资讯",
                "pic_url": "https://via.placeholder.com/300x200",
                "url": "https://www.example.com/news/2"
            }
        ]
        return build_news_response(to_user, from_user, articles)
    
    # 文本响应示例
    elif event_key == "MENU_ABOUT":
        return build_text_response(
            to_user,
            from_user,
            "👋 关于我们\n\n我们是一个创新的团队，致力于提供优质的服务。\n\n🌟 使命：让世界更美好\n💪 愿景：成为行业领导者"
        )
    
    elif event_key == "MENU_CONTACT":
        return build_text_response(
            to_user,
            from_user,
            "📞 联系我们\n\n📧 邮箱: contact@example.com\n📱 电话: 400-123-4567\n🏢 地址: 北京市朝阳区xxx大厦"
        )
    
    elif event_key == "MENU_HELP":
        return build_text_response(
            to_user,
            from_user,
            "❓ 帮助中心\n\n欢迎使用我们的服务！\n\n• 点击菜单可以查看图片、视频、音频\n• 发送文字消息与我们互动\n• 更多功能正在开发中..."
        )
    
    elif event_key == "MENU_NOTICE":
        return build_text_response(
            to_user,
            from_user,
            "🔔 通知公告\n\n系统维护通知：\n本周六凌晨2:00-4:00进行系统升级维护，期间可能无法访问。感谢您的理解！"
        )
    
    # 默认响应
    else:
        return build_text_response(
            to_user,
            from_user,
            f"收到菜单点击: {event_key}\n\n该菜单功能正在开发中..."
        )


def handle_text_message(content: str, to_user: str, from_user: str) -> str:
    """
    处理文本消息
    
    Args:
        content: 消息内容
        to_user: 接收者OpenID
        from_user: 发送者（公众号）
        
    Returns:
        响应消息XML
    """
    logger.info(f"收到文本消息: {content}")
    
    # 简单的关键词回复
    if "你好" in content or "hi" in content.lower():
        return build_text_response(
            to_user,
            from_user,
            "👋 你好！欢迎关注我们！\n\n点击下方菜单可以查看更多功能哦~"
        )
    elif "帮助" in content:
        return build_text_response(
            to_user,
            from_user,
            "❓ 帮助信息\n\n1. 点击菜单查看图片、视频、音频\n2. 发送关键词获取相应内容\n3. 关注我们获取最新资讯"
        )
    else:
        return build_text_response(
            to_user,
            from_user,
            f"收到您的消息: {content}\n\n💡 您可以点击菜单查看更多功能！"
        )


@app.route('/wechat', methods=['GET', 'POST'])
def wechat_handler():
    """微信消息处理主入口"""
    
    # GET请求：验证服务器
    if request.method == 'GET':
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        if verify_signature(signature, timestamp, nonce):
            logger.info("服务器验证成功")
            return echostr
        else:
            logger.error("服务器验证失败")
            return 'Invalid signature', 403
    
    # POST请求：处理消息
    elif request.method == 'POST':
        try:
            xml_data = request.data.decode('utf-8')
            msg = parse_xml_message(xml_data)
            
            if not msg:
                return 'success'
            
            to_user = msg.get('FromUserName')
            from_user = msg.get('ToUserName')
            msg_type = msg.get('MsgType')
            
            response_xml = ''
            
            # 处理事件消息
            if msg_type == 'event':
                event = msg.get('Event')
                
                # 关注事件
                if event == 'subscribe':
                    response_xml = build_text_response(
                        to_user,
                        from_user,
                        "🎉 感谢关注！\n\n欢迎使用我们的服务，点击菜单可以查看更多精彩内容！"
                    )
                
                # 取消关注事件
                elif event == 'unsubscribe':
                    logger.info(f"用户取消关注: {to_user}")
                    return 'success'
                
                # 菜单点击事件
                elif event == 'CLICK':
                    event_key = msg.get('EventKey')
                    response_xml = handle_menu_click(event_key, to_user, from_user)
            
            # 处理文本消息
            elif msg_type == 'text':
                content = msg.get('Content', '')
                response_xml = handle_text_message(content, to_user, from_user)
            
            # 其他消息类型
            else:
                response_xml = build_text_response(
                    to_user,
                    from_user,
                    "感谢您的消息！我们已收到。"
                )
            
            # 返回响应
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response
            
        except Exception as e:
            logger.error(f"处理消息异常: {e}", exc_info=True)
            return 'success'


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return {
        'status': 'ok',
        'timestamp': int(time.time())
    }


def main():
    """主函数"""
    global config, menu_manager
    
    print("🚀 微信公众号消息响应服务器")
    print("=" * 60)
    
    try:
        # 加载配置
        config = load_config()
        print("✅ 配置文件加载成功")
        
        # 初始化菜单管理器
        menu_manager = WeChatOfficialMenuManager()
        print("✅ 菜单管理器初始化成功")
        
        # 获取服务器配置
        host = config.get('SERVER', 'host')
        port = config.getint('SERVER', 'port')
        debug = config.getboolean('SERVER', 'debug')
        
        print(f"\n📡 服务器配置:")
        print(f"   地址: {host}:{port}")
        print(f"   调试模式: {debug}")
        print(f"\n💡 请在微信公众平台配置服务器地址:")
        print(f"   URL: http://your-domain:{port}/wechat")
        print(f"   Token: {config.get('WECHAT_OFFICIAL', 'token')}")
        print("\n" + "=" * 60)
        print("🎯 服务器启动中...\n")
        
        # 启动服务器
        app.run(host=host, port=port, debug=debug)
        
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("💡 请先配置 wechat_official_account_config.ini 文件")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.error(f"服务器启动失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()
