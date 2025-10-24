"""
个人地址模块 - 数据模型
支持多地址管理、自动识别和填充功能
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re
import json
from datetime import datetime


class AddressType(Enum):
    """地址类型枚举"""
    HOME = "home"           # 家庭地址
    WORK = "work"           # 工作地址
    BILLING = "billing"     # 账单地址
    SHIPPING = "shipping"   # 收货地址
    OTHER = "other"         # 其他地址


class AddressStatus(Enum):
    """地址状态枚举"""
    ACTIVE = "active"       # 有效地址
    INACTIVE = "inactive"   # 无效地址
    VERIFIED = "verified"   # 已验证地址
    PENDING = "pending"     # 待验证地址


@dataclass
class AddressComponent:
    """地址组件"""
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    room: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}


@dataclass
class Address:
    """地址实体"""
    id: str
    user_id: str
    address_type: AddressType
    status: AddressStatus = AddressStatus.ACTIVE
    is_default: bool = False
    label: Optional[str] = None  # 地址标签，如"家"、"公司"等
    
    # 地址信息
    full_address: str = ""
    components: AddressComponent = field(default_factory=AddressComponent)
    
    # 联系信息
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None
    
    # 扩展信息
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address_type": self.address_type.value,
            "status": self.status.value,
            "is_default": self.is_default,
            "label": self.label,
            "full_address": self.full_address,
            "components": {
                "country": self.components.country,
                "province": self.components.province,
                "city": self.components.city,
                "district": self.components.district,
                "street": self.components.street,
                "building": self.components.building,
                "room": self.components.room,
                "postal_code": self.components.postal_code,
                "coordinates": self.components.coordinates
            },
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """从字典创建地址对象"""
        components_data = data.get("components", {})
        components = AddressComponent(
            country=components_data.get("country"),
            province=components_data.get("province"),
            city=components_data.get("city"),
            district=components_data.get("district"),
            street=components_data.get("street"),
            building=components_data.get("building"),
            room=components_data.get("room"),
            postal_code=components_data.get("postal_code"),
            coordinates=components_data.get("coordinates")
        )
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            address_type=AddressType(data["address_type"]),
            status=AddressStatus(data["status"]),
            is_default=data.get("is_default", False),
            label=data.get("label"),
            full_address=data.get("full_address", ""),
            components=components,
            contact_name=data.get("contact_name"),
            contact_phone=data.get("contact_phone"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            verified_at=datetime.fromisoformat(data["verified_at"]) if data.get("verified_at") else None,
            metadata=data.get("metadata", {})
        )


@dataclass
class User:
    """用户实体"""
    id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    addresses: List[Address] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_address(self, address: Address) -> None:
        """添加地址"""
        # 如果是默认地址，先将其他同类型地址设为非默认
        if address.is_default:
            for existing_address in self.addresses:
                if (existing_address.address_type == address.address_type and 
                    existing_address.is_default):
                    existing_address.is_default = False
        
        self.addresses.append(address)
        self.updated_at = datetime.now()
    
    def remove_address(self, address_id: str) -> bool:
        """删除地址"""
        for i, address in enumerate(self.addresses):
            if address.id == address_id:
                del self.addresses[i]
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_addresses_by_type(self, address_type: AddressType) -> List[Address]:
        """根据类型获取地址列表"""
        return [addr for addr in self.addresses if addr.address_type == address_type]
    
    def get_default_address(self, address_type: AddressType) -> Optional[Address]:
        """获取指定类型的默认地址"""
        for address in self.addresses:
            if (address.address_type == address_type and 
                address.is_default and 
                address.status == AddressStatus.ACTIVE):
                return address
        return None
    
    def set_default_address(self, address_id: str) -> bool:
        """设置默认地址"""
        target_address = None
        for address in self.addresses:
            if address.id == address_id:
                target_address = address
                break
        
        if not target_address:
            return False
        
        # 将同类型的其他地址设为非默认
        for address in self.addresses:
            if (address.address_type == target_address.address_type and 
                address.id != address_id):
                address.is_default = False
        
        target_address.is_default = True
        target_address.updated_at = datetime.now()
        self.updated_at = datetime.now()
        return True


@dataclass
class AddressParseResult:
    """地址解析结果"""
    success: bool
    full_address: str
    components: AddressComponent
    confidence: float  # 解析置信度 0-1
    suggestions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "full_address": self.full_address,
            "components": {
                "country": self.components.country,
                "province": self.components.province,
                "city": self.components.city,
                "district": self.components.district,
                "street": self.components.street,
                "building": self.components.building,
                "room": self.components.room,
                "postal_code": self.components.postal_code,
                "coordinates": self.components.coordinates
            },
            "confidence": self.confidence,
            "suggestions": self.suggestions,
            "errors": self.errors
        }