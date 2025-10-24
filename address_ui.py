"""
个人地址模块 - 前端界面
提供地址管理的用户界面组件
"""

import json
from typing import List, Dict, Optional, Callable, Any
from dataclasses import asdict
from datetime import datetime

from address_models import Address, AddressType, AddressStatus, User
from address_api import AddressAPI


class AddressUI:
    """地址管理界面"""
    
    def __init__(self, api: AddressAPI):
        self.api = api
        self.current_user_id: Optional[str] = None
    
    def set_current_user(self, user_id: str):
        """设置当前用户"""
        self.current_user_id = user_id
    
    def display_welcome(self):
        """显示欢迎界面"""
        print("=" * 50)
        print("🏠 个人地址管理系统")
        print("=" * 50)
        print("功能说明：")
        print("1. 自动识别和解析地址信息")
        print("2. 支持多种地址类型（家庭、工作、账单、收货等）")
        print("3. 智能地址建议和验证")
        print("4. 多地址管理和默认地址设置")
        print("5. 地址搜索和地理编码")
        print("=" * 50)
    
    def display_main_menu(self):
        """显示主菜单"""
        print("\n📋 主菜单")
        print("1. 添加地址")
        print("2. 查看地址列表")
        print("3. 搜索地址")
        print("4. 设置默认地址")
        print("5. 编辑地址")
        print("6. 删除地址")
        print("7. 地址验证")
        print("8. 地址建议")
        print("9. 地理编码")
        print("0. 退出")
        print("-" * 30)
    
    def display_address_types(self):
        """显示地址类型选择"""
        print("\n📍 地址类型")
        for i, addr_type in enumerate(AddressType, 1):
            type_names = {
                AddressType.HOME: "家庭地址",
                AddressType.WORK: "工作地址", 
                AddressType.BILLING: "账单地址",
                AddressType.SHIPPING: "收货地址",
                AddressType.OTHER: "其他地址"
            }
            print(f"{i}. {type_names[addr_type]}")
        print("0. 返回")
    
    def get_user_input(self, prompt: str, required: bool = True) -> str:
        """获取用户输入"""
        while True:
            value = input(f"{prompt}: ").strip()
            if value or not required:
                return value
            print("❌ 此字段为必填项，请重新输入")
    
    def get_choice(self, prompt: str, max_choice: int) -> int:
        """获取用户选择"""
        while True:
            try:
                choice = int(input(f"{prompt} (0-{max_choice}): "))
                if 0 <= choice <= max_choice:
                    return choice
                print(f"❌ 请输入 0-{max_choice} 之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def add_address_flow(self):
        """添加地址流程"""
        print("\n➕ 添加新地址")
        print("-" * 30)
        
        # 选择地址类型
        self.display_address_types()
        type_choice = self.get_choice("请选择地址类型", len(AddressType))
        if type_choice == 0:
            return
        
        address_type = list(AddressType)[type_choice - 1]
        
        # 输入地址信息
        raw_address = self.get_user_input("请输入完整地址")
        label = self.get_user_input("地址标签（可选，如：家、公司）", required=False)
        contact_name = self.get_user_input("联系人姓名（可选）", required=False)
        contact_phone = self.get_user_input("联系电话（可选）", required=False)
        
        # 是否设为默认地址
        is_default_input = input("是否设为默认地址？(y/n): ").strip().lower()
        is_default = is_default_input in ['y', 'yes', '是']
        
        # 调用API添加地址
        result = self.api.add_address({
            "user_id": self.current_user_id,
            "raw_address": raw_address,
            "address_type": address_type.value,
            "label": label,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "is_default": is_default
        })
        
        if result["success"]:
            print("✅ 地址添加成功！")
            self.display_address_details(result["address"])
            
            # 显示解析结果
            parse_result = result["parse_result"]
            if parse_result["confidence"] < 0.8:
                print(f"\n⚠️  地址解析置信度: {parse_result['confidence']:.2f}")
                if parse_result["suggestions"]:
                    print("💡 建议:")
                    for suggestion in parse_result["suggestions"]:
                        print(f"   • {suggestion}")
        else:
            print(f"❌ 地址添加失败: {result['error']}")
            if "suggestions" in result:
                print("💡 建议:")
                for suggestion in result["suggestions"]:
                    print(f"   • {suggestion}")
    
    def display_address_list(self, addresses: List[Dict[str, Any]]):
        """显示地址列表"""
        if not addresses:
            print("📭 暂无地址")
            return
        
        print(f"\n📋 地址列表 (共 {len(addresses)} 个)")
        print("-" * 50)
        
        for i, address in enumerate(addresses, 1):
            print(f"{i}. {address['label'] or '未命名地址'}")
            print(f"   类型: {self.get_address_type_name(address['address_type'])}")
            print(f"   地址: {address['full_address']}")
            if address['contact_name']:
                print(f"   联系人: {address['contact_name']}")
            if address['contact_phone']:
                print(f"   电话: {address['contact_phone']}")
            if address['is_default']:
                print("   ⭐ 默认地址")
            print()
    
    def get_address_type_name(self, address_type: str) -> str:
        """获取地址类型中文名称"""
        type_names = {
            "home": "家庭地址",
            "work": "工作地址",
            "billing": "账单地址", 
            "shipping": "收货地址",
            "other": "其他地址"
        }
        return type_names.get(address_type, address_type)
    
    def display_address_details(self, address: Dict[str, Any]):
        """显示地址详情"""
        print("\n📍 地址详情")
        print("-" * 30)
        print(f"ID: {address['id']}")
        print(f"标签: {address['label'] or '未命名'}")
        print(f"类型: {self.get_address_type_name(address['address_type'])}")
        print(f"状态: {address['status']}")
        print(f"完整地址: {address['full_address']}")
        
        components = address['components']
        print("\n📋 地址组件:")
        if components['country']:
            print(f"  国家: {components['country']}")
        if components['province']:
            print(f"  省份: {components['province']}")
        if components['city']:
            print(f"  城市: {components['city']}")
        if components['district']:
            print(f"  区县: {components['district']}")
        if components['street']:
            print(f"  街道: {components['street']}")
        if components['building']:
            print(f"  建筑物: {components['building']}")
        if components['room']:
            print(f"  房间: {components['room']}")
        if components['postal_code']:
            print(f"  邮编: {components['postal_code']}")
        if components['coordinates']:
            print(f"  坐标: {components['coordinates']}")
        
        if address['contact_name']:
            print(f"\n👤 联系人: {address['contact_name']}")
        if address['contact_phone']:
            print(f"📞 电话: {address['contact_phone']}")
        
        if address['is_default']:
            print("\n⭐ 这是默认地址")
    
    def view_addresses_flow(self):
        """查看地址流程"""
        print("\n📋 查看地址列表")
        print("-" * 30)
        
        # 选择查看方式
        print("1. 查看所有地址")
        print("2. 按类型查看")
        print("0. 返回")
        
        choice = self.get_choice("请选择", 2)
        if choice == 0:
            return
        
        if choice == 1:
            # 查看所有地址
            result = self.api.get_addresses(self.current_user_id)
            if result["success"]:
                self.display_address_list(result["addresses"])
            else:
                print(f"❌ 获取地址失败: {result['error']}")
        
        elif choice == 2:
            # 按类型查看
            self.display_address_types()
            type_choice = self.get_choice("请选择地址类型", len(AddressType))
            if type_choice == 0:
                return
            
            address_type = list(AddressType)[type_choice - 1]
            result = self.api.get_addresses(self.current_user_id, address_type.value)
            if result["success"]:
                self.display_address_list(result["addresses"])
            else:
                print(f"❌ 获取地址失败: {result['error']}")
    
    def search_addresses_flow(self):
        """搜索地址流程"""
        print("\n🔍 搜索地址")
        print("-" * 30)
        
        query = self.get_user_input("请输入搜索关键词")
        result = self.api.search_addresses(self.current_user_id, query)
        
        if result["success"]:
            addresses = result["addresses"]
            if addresses:
                print(f"\n🔍 搜索结果 (共 {len(addresses)} 个)")
                self.display_address_list(addresses)
            else:
                print("📭 未找到匹配的地址")
        else:
            print(f"❌ 搜索失败: {result['error']}")
    
    def set_default_address_flow(self):
        """设置默认地址流程"""
        print("\n⭐ 设置默认地址")
        print("-" * 30)
        
        # 获取用户所有地址
        result = self.api.get_addresses(self.current_user_id)
        if not result["success"]:
            print(f"❌ 获取地址失败: {result['error']}")
            return
        
        addresses = result["addresses"]
        if not addresses:
            print("📭 暂无地址，请先添加地址")
            return
        
        # 显示地址列表
        self.display_address_list(addresses)
        
        # 选择要设为默认的地址
        choice = self.get_choice("请选择要设为默认的地址", len(addresses))
        if choice == 0:
            return
        
        selected_address = addresses[choice - 1]
        result = self.api.set_default_address(self.current_user_id, selected_address["id"])
        
        if result["success"]:
            print("✅ 默认地址设置成功！")
        else:
            print(f"❌ 设置失败: {result['error']}")
    
    def validate_address_flow(self):
        """地址验证流程"""
        print("\n✅ 地址验证")
        print("-" * 30)
        
        address = self.get_user_input("请输入要验证的地址")
        result = self.api.validate_address(address)
        
        if result["success"]:
            validation_result = result["result"]
            parse_result = validation_result["parse_result"]
            
            print(f"\n📊 验证结果")
            print(f"地址有效性: {'✅ 有效' if validation_result['is_valid'] else '❌ 无效'}")
            print(f"解析置信度: {parse_result['confidence']:.2f}")
            
            if parse_result["components"]:
                print("\n📋 解析结果:")
                components = parse_result["components"]
                if components["country"]:
                    print(f"  国家: {components['country']}")
                if components["province"]:
                    print(f"  省份: {components['province']}")
                if components["city"]:
                    print(f"  城市: {components['city']}")
                if components["district"]:
                    print(f"  区县: {components['district']}")
                if components["street"]:
                    print(f"  街道: {components['street']}")
            
            if parse_result["suggestions"]:
                print("\n💡 建议:")
                for suggestion in parse_result["suggestions"]:
                    print(f"   • {suggestion}")
        else:
            print(f"❌ 验证失败: {result['error']}")
    
    def suggest_addresses_flow(self):
        """地址建议流程"""
        print("\n💡 地址建议")
        print("-" * 30)
        
        partial_address = self.get_user_input("请输入部分地址")
        result = self.api.suggest_addresses(partial_address)
        
        if result["success"]:
            suggestions = result["suggestions"]
            if suggestions:
                print(f"\n💡 地址建议:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
            else:
                print("📭 暂无建议")
        else:
            print(f"❌ 获取建议失败: {result['error']}")
    
    def geocode_flow(self):
        """地理编码流程"""
        print("\n🗺️  地理编码")
        print("-" * 30)
        
        print("1. 地址转坐标")
        print("2. 坐标转地址")
        print("0. 返回")
        
        choice = self.get_choice("请选择", 2)
        if choice == 0:
            return
        
        if choice == 1:
            # 地址转坐标
            address = self.get_user_input("请输入地址")
            result = self.api.geocode_address(address)
            
            if result["success"]:
                coords = result["coordinates"]
                print(f"✅ 地理编码成功!")
                print(f"纬度: {coords['lat']}")
                print(f"经度: {coords['lng']}")
            else:
                print(f"❌ 地理编码失败: {result['error']}")
        
        elif choice == 2:
            # 坐标转地址
            try:
                lat = float(input("请输入纬度: "))
                lng = float(input("请输入经度: "))
                
                result = self.api.reverse_geocode(lat, lng)
                
                if result["success"]:
                    print(f"✅ 逆地理编码成功!")
                    print(f"地址: {result['address']}")
                else:
                    print(f"❌ 逆地理编码失败: {result['error']}")
            except ValueError:
                print("❌ 请输入有效的坐标")
    
    def run(self):
        """运行主程序"""
        self.display_welcome()
        
        # 创建或选择用户
        username = self.get_user_input("请输入用户名")
        user_result = self.api.create_user({"username": username})
        if user_result["success"]:
            self.current_user_id = user_result["user"]["id"]
            print(f"✅ 欢迎, {username}!")
        else:
            print(f"❌ 用户创建失败: {user_result['error']}")
            return
        
        # 主循环
        while True:
            self.display_main_menu()
            choice = self.get_choice("请选择操作", 9)
            
            if choice == 0:
                print("👋 再见!")
                break
            elif choice == 1:
                self.add_address_flow()
            elif choice == 2:
                self.view_addresses_flow()
            elif choice == 3:
                self.search_addresses_flow()
            elif choice == 4:
                self.set_default_address_flow()
            elif choice == 5:
                print("📝 编辑地址功能开发中...")
            elif choice == 6:
                print("🗑️  删除地址功能开发中...")
            elif choice == 7:
                self.validate_address_flow()
            elif choice == 8:
                self.suggest_addresses_flow()
            elif choice == 9:
                self.geocode_flow()
            
            input("\n按回车键继续...")


if __name__ == "__main__":
    # 创建API实例
    api = AddressAPI()
    
    # 创建UI实例并运行
    ui = AddressUI(api)
    ui.run()