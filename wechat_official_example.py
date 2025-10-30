#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号菜单管理完整示例
展示如何使用菜单管理和媒体上传功能
"""

import os
from wechat_official_menu import WeChatOfficialMenuManager


def example_1_create_simple_menu():
    """示例1：创建简单菜单"""
    print("\n" + "=" * 60)
    print("示例1：创建简单菜单")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 定义菜单结构
    menu_data = {
        "button": [
            {
                "type": "click",
                "name": "点击按钮",
                "key": "SIMPLE_CLICK"
            },
            {
                "type": "view",
                "name": "访问网页",
                "url": "https://www.example.com"
            }
        ]
    }
    
    if manager.create_menu(menu_data):
        print("✅ 简单菜单创建成功！")
    else:
        print("❌ 菜单创建失败")


def example_2_create_multi_level_menu():
    """示例2：创建多级菜单"""
    print("\n" + "=" * 60)
    print("示例2：创建多级菜单（带子菜单）")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 定义多级菜单结构
    menu_data = {
        "button": [
            {
                "name": "多媒体",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "查看图片",
                        "key": "VIEW_IMAGE"
                    },
                    {
                        "type": "click",
                        "name": "观看视频",
                        "key": "VIEW_VIDEO"
                    },
                    {
                        "type": "click",
                        "name": "听音频",
                        "key": "VIEW_AUDIO"
                    }
                ]
            },
            {
                "name": "服务",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "客服支持",
                        "key": "CUSTOMER_SERVICE"
                    },
                    {
                        "type": "view",
                        "name": "在线咨询",
                        "url": "https://www.example.com/chat"
                    }
                ]
            },
            {
                "type": "click",
                "name": "关于我们",
                "key": "ABOUT_US"
            }
        ]
    }
    
    if manager.create_menu(menu_data):
        print("✅ 多级菜单创建成功！")
    else:
        print("❌ 菜单创建失败")


def example_3_upload_media():
    """示例3：上传媒体文件"""
    print("\n" + "=" * 60)
    print("示例3：上传媒体文件")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 上传图片
    print("\n📸 上传图片...")
    image_path = "./media/images/sample.jpg"
    if os.path.exists(image_path):
        media_id = manager.upload_media(image_path, 'image')
        if media_id:
            print(f"✅ 图片上传成功！Media ID: {media_id}")
        else:
            print("❌ 图片上传失败")
    else:
        print(f"⚠️  图片文件不存在: {image_path}")
    
    # 上传视频
    print("\n🎬 上传视频...")
    video_path = "./media/videos/sample.mp4"
    if os.path.exists(video_path):
        media_id = manager.upload_media(video_path, 'video')
        if media_id:
            print(f"✅ 视频上传成功！Media ID: {media_id}")
        else:
            print("❌ 视频上传失败")
    else:
        print(f"⚠️  视频文件不存在: {video_path}")
    
    # 上传音频
    print("\n🎵 上传音频...")
    audio_path = "./media/audios/sample.mp3"
    if os.path.exists(audio_path):
        media_id = manager.upload_media(audio_path, 'voice')
        if media_id:
            print(f"✅ 音频上传成功！Media ID: {media_id}")
        else:
            print("❌ 音频上传失败")
    else:
        print(f"⚠️  音频文件不存在: {audio_path}")


def example_4_create_media_menu():
    """示例4：创建带媒体响应的完整菜单"""
    print("\n" + "=" * 60)
    print("示例4：创建带媒体响应的完整菜单")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 创建完整的媒体菜单
    menu_data = {
        "button": [
            {
                "name": "🎨 媒体中心",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "📸 精美图片",
                        "key": "MEDIA_IMAGE"
                    },
                    {
                        "type": "click",
                        "name": "🎬 精彩视频",
                        "key": "MEDIA_VIDEO"
                    },
                    {
                        "type": "click",
                        "name": "🎵 动听音乐",
                        "key": "MEDIA_AUDIO"
                    },
                    {
                        "type": "click",
                        "name": "📰 图文资讯",
                        "key": "MEDIA_NEWS"
                    }
                ]
            },
            {
                "name": "🛠️ 服务中心",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "💬 在线客服",
                        "key": "SERVICE_CHAT"
                    },
                    {
                        "type": "click",
                        "name": "❓ 常见问题",
                        "key": "SERVICE_FAQ"
                    },
                    {
                        "type": "view",
                        "name": "📞 联系我们",
                        "url": "https://www.example.com/contact"
                    }
                ]
            },
            {
                "name": "ℹ️ 关于",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "🏢 公司介绍",
                        "key": "ABOUT_COMPANY"
                    },
                    {
                        "type": "click",
                        "name": "🎯 产品服务",
                        "key": "ABOUT_PRODUCT"
                    },
                    {
                        "type": "click",
                        "name": "📢 最新动态",
                        "key": "ABOUT_NEWS"
                    },
                    {
                        "type": "view",
                        "name": "🌐 官方网站",
                        "url": "https://www.example.com"
                    }
                ]
            }
        ]
    }
    
    if manager.create_menu(menu_data):
        print("✅ 媒体菜单创建成功！")
        print("\n💡 提示：")
        print("   - 需要在服务器端配置对应的响应处理")
        print("   - 预先上传媒体文件并获取media_id")
        print("   - 在wechat_official_server.py中添加对应的事件处理")
    else:
        print("❌ 菜单创建失败")


def example_5_query_and_delete_menu():
    """示例5：查询和删除菜单"""
    print("\n" + "=" * 60)
    print("示例5：查询和删除菜单")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 查询当前菜单
    print("\n🔍 查询当前菜单...")
    menu = manager.get_menu()
    if menu:
        print("✅ 菜单查询成功：")
        import json
        print(json.dumps(menu, ensure_ascii=False, indent=2))
    else:
        print("⚠️  当前没有自定义菜单")
    
    # 询问是否删除
    print("\n是否删除当前菜单? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\n🗑️  删除菜单中...")
        if manager.delete_menu():
            print("✅ 菜单删除成功！")
        else:
            print("❌ 菜单删除失败")
    else:
        print("⏭️  跳过删除操作")


def example_6_custom_menu_builder():
    """示例6：使用菜单构建器"""
    print("\n" + "=" * 60)
    print("示例6：使用菜单构建器")
    print("=" * 60)
    
    manager = WeChatOfficialMenuManager()
    
    # 使用build_custom_menu方法
    buttons = [
        {
            "name": "功能区",
            "sub_button": [
                {"type": "click", "name": "功能1", "key": "FUNC_1"},
                {"type": "click", "name": "功能2", "key": "FUNC_2"},
                {"type": "view", "name": "功能3", "url": "https://example.com"}
            ]
        },
        {
            "type": "click",
            "name": "单一按钮",
            "key": "SINGLE_BUTTON"
        }
    ]
    
    menu_data = manager.build_custom_menu(buttons)
    
    if manager.create_menu(menu_data):
        print("✅ 使用构建器创建菜单成功！")
    else:
        print("❌ 菜单创建失败")


def show_menu():
    """显示示例菜单"""
    print("\n" + "=" * 60)
    print("🎯 微信公众号菜单管理示例")
    print("=" * 60)
    print("\n请选择要运行的示例：")
    print("\n1. 创建简单菜单")
    print("2. 创建多级菜单")
    print("3. 上传媒体文件")
    print("4. 创建带媒体响应的完整菜单")
    print("5. 查询和删除菜单")
    print("6. 使用菜单构建器")
    print("7. 创建预设示例菜单")
    print("0. 退出")
    print("\n" + "=" * 60)


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("\n请输入选项 (0-7): ").strip()
        
        try:
            if choice == '1':
                example_1_create_simple_menu()
            elif choice == '2':
                example_2_create_multi_level_menu()
            elif choice == '3':
                example_3_upload_media()
            elif choice == '4':
                example_4_create_media_menu()
            elif choice == '5':
                example_5_query_and_delete_menu()
            elif choice == '6':
                example_6_custom_menu_builder()
            elif choice == '7':
                manager = WeChatOfficialMenuManager()
                manager.create_example_menu()
            elif choice == '0':
                print("\n👋 再见！")
                break
            else:
                print("\n⚠️  无效的选项，请重新输入")
            
            input("\n按Enter键继续...")
            
        except FileNotFoundError as e:
            print(f"\n❌ 错误: {e}")
            print("💡 请先配置 wechat_official_account_config.ini 文件")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            input("\n按Enter键继续...")


if __name__ == "__main__":
    main()
