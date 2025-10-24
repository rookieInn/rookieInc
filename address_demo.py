"""
个人地址模块 - 使用示例和测试
演示地址模块的各种功能
"""

import json
from datetime import datetime
from address_models import AddressType, AddressStatus
from address_api import AddressAPI
from address_parser import AddressParser, AddressValidator


def demo_address_parsing():
    """演示地址解析功能"""
    print("=" * 60)
    print("🔍 地址解析功能演示")
    print("=" * 60)
    
    parser = AddressParser()
    
    # 测试地址列表
    test_addresses = [
        "北京市朝阳区建国门外大街1号国贸大厦A座1001室",
        "上海市浦东新区陆家嘴环路1000号恒生银行大厦",
        "深圳市南山区科技园南区深南大道10000号腾讯大厦",
        "广州市天河区珠江新城花城大道85号高德置地广场",
        "杭州市西湖区文三路259号昌地火炬大厦",
        "张三 北京市海淀区中关村大街27号 13800138000",
        "李四 上海市黄浦区南京东路399号 021-12345678",
        "王五 深圳市福田区华强北路1号赛格广场"
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n📍 测试地址 {i}: {address}")
        print("-" * 50)
        
        result = parser.parse_address(address)
        
        print(f"解析成功: {'✅' if result.success else '❌'}")
        print(f"置信度: {result.confidence:.2f}")
        print(f"完整地址: {result.full_address}")
        
        if result.components:
            components = result.components
            print("解析组件:")
            if components.country:
                print(f"  国家: {components.country}")
            if components.province:
                print(f"  省份: {components.province}")
            if components.city:
                print(f"  城市: {components.city}")
            if components.district:
                print(f"  区县: {components.district}")
            if components.street:
                print(f"  街道: {components.street}")
            if components.building:
                print(f"  建筑物: {components.building}")
            if components.room:
                print(f"  房间: {components.room}")
            if components.postal_code:
                print(f"  邮编: {components.postal_code}")
        
        if result.suggestions:
            print("建议:")
            for suggestion in result.suggestions:
                print(f"  • {suggestion}")
        
        if result.errors:
            print("错误:")
            for error in result.errors:
                print(f"  • {error}")


def demo_address_validation():
    """演示地址验证功能"""
    print("\n" + "=" * 60)
    print("✅ 地址验证功能演示")
    print("=" * 60)
    
    validator = AddressValidator()
    
    # 测试数据
    test_cases = [
        ("北京市朝阳区建国门外大街1号", True),
        ("上海市浦东新区陆家嘴环路1000号", True),
        ("深圳", False),  # 太短
        ("", False),  # 空地址
        ("123456", False),  # 不是地址
        ("北京市朝阳区建国门外大街1号国贸大厦A座1001室", True),
    ]
    
    for address, expected in test_cases:
        is_valid = validator.validate_address_format(address)
        status = "✅" if is_valid == expected else "❌"
        print(f"{status} 地址: {address}")
        print(f"   验证结果: {'有效' if is_valid else '无效'}")
        print(f"   预期结果: {'有效' if expected else '无效'}")
        print()
    
    # 测试邮政编码验证
    print("📮 邮政编码验证:")
    postal_codes = ["100000", "200000", "12345", "1234567", "abc123"]
    for code in postal_codes:
        is_valid = validator.validate_postal_code(code)
        print(f"  {code}: {'✅' if is_valid else '❌'}")
    
    # 测试电话号码验证
    print("\n📞 电话号码验证:")
    phone_numbers = [
        "13800138000",  # 手机号
        "021-12345678",  # 固定电话
        "02112345678",  # 无分隔符固定电话
        "12345678901",  # 无效手机号
        "abc12345678"   # 无效格式
    ]
    for phone in phone_numbers:
        is_valid = validator.validate_phone(phone)
        print(f"  {phone}: {'✅' if is_valid else '❌'}")


def demo_address_management():
    """演示地址管理功能"""
    print("\n" + "=" * 60)
    print("🏠 地址管理功能演示")
    print("=" * 60)
    
    api = AddressAPI()
    
    # 创建用户
    print("👤 创建用户...")
    user_result = api.create_user({
        "username": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000"
    })
    
    if not user_result["success"]:
        print(f"❌ 用户创建失败: {user_result['error']}")
        return
    
    user_id = user_result["user"]["id"]
    print(f"✅ 用户创建成功: {user_result['user']['username']}")
    
    # 添加多个地址
    addresses_data = [
        {
            "raw_address": "北京市朝阳区建国门外大街1号国贸大厦A座1001室",
            "address_type": "home",
            "label": "家",
            "contact_name": "张三",
            "contact_phone": "13800138000",
            "is_default": True
        },
        {
            "raw_address": "上海市浦东新区陆家嘴环路1000号恒生银行大厦",
            "address_type": "work",
            "label": "公司",
            "contact_name": "张三",
            "contact_phone": "021-12345678",
            "is_default": False
        },
        {
            "raw_address": "深圳市南山区科技园南区深南大道10000号腾讯大厦",
            "address_type": "shipping",
            "label": "收货地址",
            "contact_name": "张三",
            "contact_phone": "0755-12345678",
            "is_default": False
        }
    ]
    
    print("\n📍 添加地址...")
    for i, addr_data in enumerate(addresses_data, 1):
        addr_data["user_id"] = user_id
        result = api.add_address(addr_data)
        
        if result["success"]:
            print(f"✅ 地址 {i} 添加成功")
            print(f"   标签: {result['address']['label']}")
            print(f"   类型: {result['address']['address_type']}")
            print(f"   地址: {result['address']['full_address']}")
            print(f"   解析置信度: {result['parse_result']['confidence']:.2f}")
        else:
            print(f"❌ 地址 {i} 添加失败: {result['error']}")
        print()
    
    # 查看所有地址
    print("📋 查看所有地址...")
    result = api.get_addresses(user_id)
    if result["success"]:
        addresses = result["addresses"]
        print(f"共找到 {len(addresses)} 个地址:")
        for i, addr in enumerate(addresses, 1):
            print(f"{i}. {addr['label']} ({addr['address_type']})")
            print(f"   {addr['full_address']}")
            if addr['is_default']:
                print("   ⭐ 默认地址")
            print()
    
    # 按类型查看地址
    print("📋 按类型查看地址...")
    for addr_type in ["home", "work", "shipping"]:
        result = api.get_addresses(user_id, addr_type)
        if result["success"]:
            addresses = result["addresses"]
            print(f"{addr_type} 类型地址 ({len(addresses)} 个):")
            for addr in addresses:
                print(f"  • {addr['label']}: {addr['full_address']}")
            print()
    
    # 搜索地址
    print("🔍 搜索地址...")
    search_queries = ["北京", "上海", "公司", "家"]
    for query in search_queries:
        result = api.search_addresses(user_id, query)
        if result["success"]:
            addresses = result["addresses"]
            print(f"搜索 '{query}' 找到 {len(addresses)} 个结果:")
            for addr in addresses:
                print(f"  • {addr['label']}: {addr['full_address']}")
            print()
    
    # 设置默认地址
    print("⭐ 设置默认地址...")
    result = api.get_addresses(user_id, "work")
    if result["success"] and result["addresses"]:
        work_address = result["addresses"][0]
        result = api.set_default_address(user_id, work_address["id"])
        if result["success"]:
            print(f"✅ 已将工作地址设为默认: {work_address['label']}")
        else:
            print(f"❌ 设置默认地址失败: {result['error']}")
    
    # 地址建议
    print("\n💡 地址建议...")
    partial_addresses = ["北京", "上海", "深圳", "广州"]
    for partial in partial_addresses:
        result = api.suggest_addresses(partial)
        if result["success"]:
            suggestions = result["suggestions"]
            print(f"'{partial}' 的建议地址:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
            print()
    
    # 地理编码
    print("🗺️  地理编码...")
    test_address = "北京市朝阳区建国门外大街1号"
    result = api.geocode_address(test_address)
    if result["success"]:
        coords = result["coordinates"]
        print(f"地址: {test_address}")
        print(f"坐标: 纬度 {coords['lat']}, 经度 {coords['lng']}")
    
    # 逆地理编码
    print("\n🗺️  逆地理编码...")
    result = api.reverse_geocode(39.9042, 116.4074)
    if result["success"]:
        print(f"坐标: 39.9042, 116.4074")
        print(f"地址: {result['address']}")


def demo_address_suggestions():
    """演示地址建议功能"""
    print("\n" + "=" * 60)
    print("💡 地址建议功能演示")
    print("=" * 60)
    
    parser = AddressParser()
    
    # 测试部分地址建议
    partial_addresses = [
        "北京",
        "上海",
        "深圳",
        "广州",
        "杭州",
        "南京",
        "武汉",
        "成都"
    ]
    
    for partial in partial_addresses:
        print(f"\n🔍 部分地址: '{partial}'")
        suggestions = parser.suggest_addresses(partial, limit=3)
        if suggestions:
            print("建议地址:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  暂无建议")


def run_all_demos():
    """运行所有演示"""
    print("🚀 个人地址模块功能演示")
    print("=" * 60)
    
    try:
        # 地址解析演示
        demo_address_parsing()
        
        # 地址验证演示
        demo_address_validation()
        
        # 地址管理演示
        demo_address_management()
        
        # 地址建议演示
        demo_address_suggestions()
        
        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()