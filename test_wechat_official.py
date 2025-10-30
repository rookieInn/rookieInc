#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号菜单系统测试脚本
"""

import os
import sys
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from wechat_official_menu import WeChatOfficialMenuManager


class TestWeChatOfficialMenu(unittest.TestCase):
    """菜单管理测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试配置文件
        self.test_config = 'test_wechat_config.ini'
        with open(self.test_config, 'w', encoding='utf-8') as f:
            f.write("""[WECHAT_OFFICIAL]
appid = test_appid
appsecret = test_appsecret
token = test_token
encoding_aes_key = test_aes_key

[SERVER]
host = 0.0.0.0
port = 8080
debug = false

[MEDIA]
image_path = ./test_media/images
video_path = ./test_media/videos
audio_path = ./test_media/audios

[MENU]
auto_create_example = false
""")
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_config):
            os.remove(self.test_config)
        # 清理测试媒体目录
        if os.path.exists('./test_media'):
            import shutil
            shutil.rmtree('./test_media')
    
    def test_config_loading(self):
        """测试配置文件加载"""
        manager = WeChatOfficialMenuManager(self.test_config)
        self.assertEqual(manager.appid, 'test_appid')
        self.assertEqual(manager.appsecret, 'test_appsecret')
        print("✓ 配置文件加载测试通过")
    
    def test_media_directory_creation(self):
        """测试媒体目录创建"""
        manager = WeChatOfficialMenuManager(self.test_config)
        self.assertTrue(os.path.exists('./test_media/images'))
        self.assertTrue(os.path.exists('./test_media/videos'))
        self.assertTrue(os.path.exists('./test_media/audios'))
        print("✓ 媒体目录创建测试通过")
    
    @patch('wechat_official_menu.requests.get')
    def test_get_access_token(self, mock_get):
        """测试获取access_token"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 7200
        }
        mock_get.return_value = mock_response
        
        manager = WeChatOfficialMenuManager(self.test_config)
        token = manager.get_access_token()
        
        self.assertEqual(token, 'test_token_123')
        self.assertIsNotNone(manager.access_token)
        print("✓ access_token获取测试通过")
    
    def test_build_custom_menu(self):
        """测试菜单构建"""
        manager = WeChatOfficialMenuManager(self.test_config)
        
        buttons = [
            {
                "name": "测试菜单",
                "sub_button": [
                    {"type": "click", "name": "子菜单1", "key": "KEY1"},
                    {"type": "view", "name": "子菜单2", "url": "http://example.com"}
                ]
            }
        ]
        
        menu_data = manager.build_custom_menu(buttons)
        
        self.assertIn('button', menu_data)
        self.assertEqual(len(menu_data['button']), 1)
        self.assertEqual(menu_data['button'][0]['name'], '测试菜单')
        print("✓ 菜单构建测试通过")
    
    def test_menu_button_limit(self):
        """测试菜单数量限制"""
        manager = WeChatOfficialMenuManager(self.test_config)
        
        # 测试超过3个一级菜单
        buttons = [
            {"type": "click", "name": f"菜单{i}", "key": f"KEY{i}"}
            for i in range(5)
        ]
        
        menu_data = manager.build_custom_menu(buttons)
        self.assertEqual(len(menu_data['button']), 3)  # 应该只有3个
        print("✓ 菜单数量限制测试通过")
    
    @patch('wechat_official_menu.requests.post')
    @patch('wechat_official_menu.requests.get')
    def test_create_menu(self, mock_get, mock_post):
        """测试创建菜单"""
        # 模拟token获取
        mock_get_response = Mock()
        mock_get_response.json.return_value = {
            'access_token': 'test_token',
            'expires_in': 7200
        }
        mock_get.return_value = mock_get_response
        
        # 模拟创建菜单成功
        mock_post_response = Mock()
        mock_post_response.json.return_value = {'errcode': 0, 'errmsg': 'ok'}
        mock_post.return_value = mock_post_response
        
        manager = WeChatOfficialMenuManager(self.test_config)
        menu_data = {
            "button": [
                {"type": "click", "name": "测试", "key": "TEST"}
            ]
        }
        
        result = manager.create_menu(menu_data)
        self.assertTrue(result)
        print("✓ 创建菜单测试通过")
    
    @patch('wechat_official_menu.requests.get')
    def test_get_menu(self, mock_get):
        """测试查询菜单"""
        # 模拟token获取和菜单查询
        mock_response = Mock()
        mock_response.json.side_effect = [
            {'access_token': 'test_token', 'expires_in': 7200},
            {'menu': {'button': []}}
        ]
        mock_get.return_value = mock_response
        
        manager = WeChatOfficialMenuManager(self.test_config)
        menu = manager.get_menu()
        
        self.assertIsNotNone(menu)
        self.assertIn('menu', menu)
        print("✓ 查询菜单测试通过")
    
    @patch('wechat_official_menu.requests.get')
    def test_delete_menu(self, mock_get):
        """测试删除菜单"""
        # 模拟响应
        mock_response = Mock()
        mock_response.json.side_effect = [
            {'access_token': 'test_token', 'expires_in': 7200},
            {'errcode': 0, 'errmsg': 'ok'}
        ]
        mock_get.return_value = mock_response
        
        manager = WeChatOfficialMenuManager(self.test_config)
        result = manager.delete_menu()
        
        self.assertTrue(result)
        print("✓ 删除菜单测试通过")


class TestWeChatMessageHandling(unittest.TestCase):
    """消息处理测试"""
    
    def test_verify_signature(self):
        """测试签名验证"""
        from wechat_official_server import verify_signature
        from configparser import ConfigParser
        import hashlib
        
        # 创建临时配置
        global config
        config = ConfigParser()
        config['WECHAT_OFFICIAL'] = {'token': 'test_token'}
        
        # 生成测试签名
        timestamp = '1234567890'
        nonce = 'test_nonce'
        token = 'test_token'
        
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        signature = hashlib.sha1(''.join(tmp_list).encode('utf-8')).hexdigest()
        
        # 验证
        result = verify_signature(signature, timestamp, nonce)
        self.assertTrue(result)
        print("✓ 签名验证测试通过")
    
    def test_parse_xml_message(self):
        """测试XML解析"""
        from wechat_official_server import parse_xml_message
        
        xml_data = """<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1234567890</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[test message]]></Content>
        </xml>"""
        
        msg = parse_xml_message(xml_data)
        
        self.assertEqual(msg['ToUserName'], 'toUser')
        self.assertEqual(msg['FromUserName'], 'fromUser')
        self.assertEqual(msg['MsgType'], 'text')
        self.assertEqual(msg['Content'], 'test message')
        print("✓ XML解析测试通过")
    
    def test_build_text_response(self):
        """测试构建文本响应"""
        from wechat_official_server import build_text_response
        
        response = build_text_response('user123', 'official', '测试消息')
        
        self.assertIn('user123', response)
        self.assertIn('official', response)
        self.assertIn('测试消息', response)
        self.assertIn('<MsgType><![CDATA[text]]></MsgType>', response)
        print("✓ 文本响应构建测试通过")
    
    def test_build_image_response(self):
        """测试构建图片响应"""
        from wechat_official_server import build_image_response
        
        response = build_image_response('user123', 'official', 'media_id_123')
        
        self.assertIn('user123', response)
        self.assertIn('media_id_123', response)
        self.assertIn('<MsgType><![CDATA[image]]></MsgType>', response)
        print("✓ 图片响应构建测试通过")
    
    def test_build_video_response(self):
        """测试构建视频响应"""
        from wechat_official_server import build_video_response
        
        response = build_video_response(
            'user123',
            'official',
            'media_id_123',
            '视频标题',
            '视频描述'
        )
        
        self.assertIn('media_id_123', response)
        self.assertIn('视频标题', response)
        self.assertIn('视频描述', response)
        self.assertIn('<MsgType><![CDATA[video]]></MsgType>', response)
        print("✓ 视频响应构建测试通过")
    
    def test_build_voice_response(self):
        """测试构建语音响应"""
        from wechat_official_server import build_voice_response
        
        response = build_voice_response('user123', 'official', 'media_id_123')
        
        self.assertIn('media_id_123', response)
        self.assertIn('<MsgType><![CDATA[voice]]></MsgType>', response)
        print("✓ 语音响应构建测试通过")
    
    def test_build_news_response(self):
        """测试构建图文响应"""
        from wechat_official_server import build_news_response
        
        articles = [
            {
                'title': '标题1',
                'description': '描述1',
                'pic_url': 'http://example.com/pic1.jpg',
                'url': 'http://example.com/article1'
            }
        ]
        
        response = build_news_response('user123', 'official', articles)
        
        self.assertIn('标题1', response)
        self.assertIn('描述1', response)
        self.assertIn('<MsgType><![CDATA[news]]></MsgType>', response)
        self.assertIn('<ArticleCount>1</ArticleCount>', response)
        print("✓ 图文响应构建测试通过")


def run_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 微信公众号菜单系统测试")
    print("=" * 60 + "\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestWeChatOfficialMenu))
    suite.addTests(loader.loadTestsFromTestCase(TestWeChatMessageHandling))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
    print("=" * 60 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
