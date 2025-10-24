"""
个人地址模块 - API接口
提供地址管理的RESTful API
"""

from typing import List, Dict, Optional, Any
from dataclasses import asdict
from datetime import datetime
import json
import uuid

from address_models import (
    User, Address, AddressType, AddressStatus, 
    AddressComponent, AddressParseResult
)
from address_parser import AddressParser, AddressValidator


class AddressService:
    """地址服务类"""
    
    def __init__(self):
        self.parser = AddressParser()
        self.validator = AddressValidator()
        self.users: Dict[str, User] = {}
        self.addresses: Dict[str, Address] = {}
    
    def create_user(self, username: str, email: Optional[str] = None, 
                   phone: Optional[str] = None) -> User:
        """创建用户"""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email,
            phone=phone
        )
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        return self.users.get(user_id)
    
    def parse_address(self, raw_address: str) -> AddressParseResult:
        """解析地址"""
        return self.parser.parse_address(raw_address)
    
    def add_address(self, user_id: str, raw_address: str, 
                   address_type: AddressType, label: Optional[str] = None,
                   contact_name: Optional[str] = None, 
                   contact_phone: Optional[str] = None,
                   is_default: bool = False) -> Dict[str, Any]:
        """添加地址"""
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "error": "用户不存在"}
        
        # 解析地址
        parse_result = self.parse_address(raw_address)
        if not parse_result.success:
            return {
                "success": False, 
                "error": "地址解析失败", 
                "details": parse_result.errors,
                "suggestions": parse_result.suggestions
            }
        
        # 验证联系信息
        if contact_phone and not self.validator.validate_phone(contact_phone):
            return {"success": False, "error": "电话号码格式不正确"}
        
        # 创建地址对象
        address_id = str(uuid.uuid4())
        address = Address(
            id=address_id,
            user_id=user_id,
            address_type=address_type,
            status=AddressStatus.ACTIVE,
            is_default=is_default,
            label=label,
            full_address=parse_result.full_address,
            components=parse_result.components,
            contact_name=contact_name,
            contact_phone=contact_phone
        )
        
        # 添加到用户
        user.add_address(address)
        self.addresses[address_id] = address
        
        return {
            "success": True,
            "address": address.to_dict(),
            "parse_result": parse_result.to_dict()
        }
    
    def get_user_addresses(self, user_id: str, 
                          address_type: Optional[AddressType] = None) -> List[Dict[str, Any]]:
        """获取用户地址列表"""
        user = self.get_user(user_id)
        if not user:
            return []
        
        if address_type:
            addresses = user.get_addresses_by_type(address_type)
        else:
            addresses = user.addresses
        
        return [address.to_dict() for address in addresses]
    
    def get_address(self, address_id: str) -> Optional[Dict[str, Any]]:
        """获取单个地址"""
        address = self.addresses.get(address_id)
        return address.to_dict() if address else None
    
    def update_address(self, address_id: str, **kwargs) -> Dict[str, Any]:
        """更新地址"""
        address = self.addresses.get(address_id)
        if not address:
            return {"success": False, "error": "地址不存在"}
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(address, key):
                setattr(address, key, value)
        
        address.updated_at = datetime.now()
        
        return {"success": True, "address": address.to_dict()}
    
    def delete_address(self, address_id: str) -> Dict[str, Any]:
        """删除地址"""
        address = self.addresses.get(address_id)
        if not address:
            return {"success": False, "error": "地址不存在"}
        
        user = self.get_user(address.user_id)
        if user:
            user.remove_address(address_id)
        
        del self.addresses[address_id]
        
        return {"success": True}
    
    def set_default_address(self, user_id: str, address_id: str) -> Dict[str, Any]:
        """设置默认地址"""
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "error": "用户不存在"}
        
        success = user.set_default_address(address_id)
        if success:
            return {"success": True}
        else:
            return {"success": False, "error": "地址不存在或设置失败"}
    
    def get_default_address(self, user_id: str, address_type: AddressType) -> Optional[Dict[str, Any]]:
        """获取默认地址"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        address = user.get_default_address(address_type)
        return address.to_dict() if address else None
    
    def search_addresses(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """搜索地址"""
        user = self.get_user(user_id)
        if not user:
            return []
        
        results = []
        query_lower = query.lower()
        
        for address in user.addresses:
            # 搜索地址内容
            if (query_lower in address.full_address.lower() or
                (address.label and query_lower in address.label.lower()) or
                (address.contact_name and query_lower in address.contact_name.lower())):
                results.append(address.to_dict())
        
        return results
    
    def suggest_addresses(self, partial_address: str, limit: int = 5) -> List[str]:
        """获取地址建议"""
        return self.parser.suggest_addresses(partial_address, limit)
    
    def validate_address(self, address: str) -> Dict[str, Any]:
        """验证地址"""
        is_valid = self.validator.validate_address_format(address)
        parse_result = self.parser.parse_address(address)
        
        return {
            "is_valid": is_valid,
            "parse_result": parse_result.to_dict(),
            "suggestions": parse_result.suggestions if not is_valid else []
        }
    
    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """地理编码"""
        return self.parser.geocode_address(address)
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """逆地理编码"""
        return self.parser.reverse_geocode(lat, lng)


class AddressAPI:
    """地址API接口"""
    
    def __init__(self):
        self.service = AddressService()
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户API"""
        try:
            user = self.service.create_user(
                username=data.get("username"),
                email=data.get("email"),
                phone=data.get("phone")
            )
            return {"success": True, "user": user.__dict__}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_address(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """添加地址API"""
        try:
            address_type = AddressType(data.get("address_type", "other"))
            result = self.service.add_address(
                user_id=data["user_id"],
                raw_address=data["raw_address"],
                address_type=address_type,
                label=data.get("label"),
                contact_name=data.get("contact_name"),
                contact_phone=data.get("contact_phone"),
                is_default=data.get("is_default", False)
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_addresses(self, user_id: str, address_type: Optional[str] = None) -> Dict[str, Any]:
        """获取地址列表API"""
        try:
            addr_type = AddressType(address_type) if address_type else None
            addresses = self.service.get_user_addresses(user_id, addr_type)
            return {"success": True, "addresses": addresses}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_address(self, address_id: str) -> Dict[str, Any]:
        """获取单个地址API"""
        try:
            address = self.service.get_address(address_id)
            if address:
                return {"success": True, "address": address}
            else:
                return {"success": False, "error": "地址不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_address(self, address_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新地址API"""
        try:
            result = self.service.update_address(address_id, **data)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_address(self, address_id: str) -> Dict[str, Any]:
        """删除地址API"""
        try:
            result = self.service.delete_address(address_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_default_address(self, user_id: str, address_id: str) -> Dict[str, Any]:
        """设置默认地址API"""
        try:
            result = self.service.set_default_address(user_id, address_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_addresses(self, user_id: str, query: str) -> Dict[str, Any]:
        """搜索地址API"""
        try:
            addresses = self.service.search_addresses(user_id, query)
            return {"success": True, "addresses": addresses}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def suggest_addresses(self, partial_address: str, limit: int = 5) -> Dict[str, Any]:
        """获取地址建议API"""
        try:
            suggestions = self.service.suggest_addresses(partial_address, limit)
            return {"success": True, "suggestions": suggestions}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_address(self, address: str) -> Dict[str, Any]:
        """验证地址API"""
        try:
            result = self.service.validate_address(address)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """地理编码API"""
        try:
            coordinates = self.service.geocode_address(address)
            if coordinates:
                return {"success": True, "coordinates": coordinates}
            else:
                return {"success": False, "error": "地理编码失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """逆地理编码API"""
        try:
            address = self.service.reverse_geocode(lat, lng)
            if address:
                return {"success": True, "address": address}
            else:
                return {"success": False, "error": "逆地理编码失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}