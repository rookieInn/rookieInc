"""
五级行政区划查询系统 - 数据模型
省、市、县、镇、村五级联动查询
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Province(Base):
    """省级行政区划表"""
    __tablename__ = 'provinces'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), unique=True, nullable=False, comment='省级行政区划代码')
    name = Column(String(50), nullable=False, comment='省级名称')
    short_name = Column(String(20), comment='简称')
    pinyin = Column(String(100), comment='拼音')
    sort_order = Column(Integer, default=0, comment='排序')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    cities = relationship("City", back_populates="province", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_name_pinyin', 'name', 'pinyin'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name,
            'pinyin': self.pinyin,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'level': 'province'
        }

class City(Base):
    """市级行政区划表"""
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), unique=True, nullable=False, comment='市级行政区划代码')
    name = Column(String(50), nullable=False, comment='市级名称')
    short_name = Column(String(20), comment='简称')
    pinyin = Column(String(100), comment='拼音')
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False, comment='所属省份ID')
    sort_order = Column(Integer, default=0, comment='排序')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    province = relationship("Province", back_populates="cities")
    counties = relationship("County", back_populates="city", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_province_id', 'province_id'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_name_pinyin', 'name', 'pinyin'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name,
            'pinyin': self.pinyin,
            'province_id': self.province_id,
            'province_name': self.province.name if self.province else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'level': 'city'
        }

class County(Base):
    """县级行政区划表"""
    __tablename__ = 'counties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), unique=True, nullable=False, comment='县级行政区划代码')
    name = Column(String(50), nullable=False, comment='县级名称')
    short_name = Column(String(20), comment='简称')
    pinyin = Column(String(100), comment='拼音')
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False, comment='所属城市ID')
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False, comment='所属省份ID')
    sort_order = Column(Integer, default=0, comment='排序')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    city = relationship("City", back_populates="counties")
    province = relationship("Province")
    towns = relationship("Town", back_populates="county", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_city_id', 'city_id'),
        Index('idx_province_id', 'province_id'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_name_pinyin', 'name', 'pinyin'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name,
            'pinyin': self.pinyin,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else None,
            'province_id': self.province_id,
            'province_name': self.province.name if self.province else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'level': 'county'
        }

class Town(Base):
    """镇级行政区划表"""
    __tablename__ = 'towns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), unique=True, nullable=False, comment='镇级行政区划代码')
    name = Column(String(50), nullable=False, comment='镇级名称')
    short_name = Column(String(20), comment='简称')
    pinyin = Column(String(100), comment='拼音')
    county_id = Column(Integer, ForeignKey('counties.id', ondelete='CASCADE'), nullable=False, comment='所属县ID')
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False, comment='所属城市ID')
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False, comment='所属省份ID')
    sort_order = Column(Integer, default=0, comment='排序')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    county = relationship("County", back_populates="towns")
    city = relationship("City")
    province = relationship("Province")
    villages = relationship("Village", back_populates="town", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_county_id', 'county_id'),
        Index('idx_city_id', 'city_id'),
        Index('idx_province_id', 'province_id'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_name_pinyin', 'name', 'pinyin'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name,
            'pinyin': self.pinyin,
            'county_id': self.county_id,
            'county_name': self.county.name if self.county else None,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else None,
            'province_id': self.province_id,
            'province_name': self.province.name if self.province else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'level': 'town'
        }

class Village(Base):
    """村级行政区划表"""
    __tablename__ = 'villages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), unique=True, nullable=False, comment='村级行政区划代码')
    name = Column(String(50), nullable=False, comment='村级名称')
    short_name = Column(String(20), comment='简称')
    pinyin = Column(String(100), comment='拼音')
    town_id = Column(Integer, ForeignKey('towns.id', ondelete='CASCADE'), nullable=False, comment='所属镇ID')
    county_id = Column(Integer, ForeignKey('counties.id', ondelete='CASCADE'), nullable=False, comment='所属县ID')
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False, comment='所属城市ID')
    province_id = Column(Integer, ForeignKey('provinces.id', ondelete='CASCADE'), nullable=False, comment='所属省份ID')
    sort_order = Column(Integer, default=0, comment='排序')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    town = relationship("Town", back_populates="villages")
    county = relationship("County")
    city = relationship("City")
    province = relationship("Province")
    
    # 索引
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_name', 'name'),
        Index('idx_town_id', 'town_id'),
        Index('idx_county_id', 'county_id'),
        Index('idx_city_id', 'city_id'),
        Index('idx_province_id', 'province_id'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_name_pinyin', 'name', 'pinyin'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name,
            'pinyin': self.pinyin,
            'town_id': self.town_id,
            'town_name': self.town.name if self.town else None,
            'county_id': self.county_id,
            'county_name': self.county.name if self.county else None,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else None,
            'province_id': self.province_id,
            'province_name': self.province.name if self.province else None,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'level': 'village'
        }

class AdministrativeQueryService:
    """行政区划查询服务"""
    
    def __init__(self, database_url="sqlite:///administrative_query.db"):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def get_provinces(self):
        """获取所有省份"""
        return self.session.query(Province).filter(Province.is_active == True).order_by(Province.sort_order, Province.name).all()
    
    def get_cities_by_province(self, province_id):
        """根据省份ID获取城市列表"""
        return self.session.query(City).filter(
            City.province_id == province_id,
            City.is_active == True
        ).order_by(City.sort_order, City.name).all()
    
    def get_counties_by_city(self, city_id):
        """根据城市ID获取区县列表"""
        return self.session.query(County).filter(
            County.city_id == city_id,
            County.is_active == True
        ).order_by(County.sort_order, County.name).all()
    
    def get_towns_by_county(self, county_id):
        """根据区县ID获取镇列表"""
        return self.session.query(Town).filter(
            Town.county_id == county_id,
            Town.is_active == True
        ).order_by(Town.sort_order, Town.name).all()
    
    def get_villages_by_town(self, town_id):
        """根据镇ID获取村列表"""
        return self.session.query(Village).filter(
            Village.town_id == town_id,
            Village.is_active == True
        ).order_by(Village.sort_order, Village.name).all()
    
    def search_administrative_divisions(self, keyword):
        """搜索行政区划"""
        results = []
        
        # 搜索省份
        provinces = self.session.query(Province).filter(
            Province.is_active == True,
            (Province.name.like(f'%{keyword}%') | Province.pinyin.like(f'%{keyword}%'))
        ).all()
        results.extend([p.to_dict() for p in provinces])
        
        # 搜索城市
        cities = self.session.query(City).join(Province).filter(
            City.is_active == True,
            (City.name.like(f'%{keyword}%') | City.pinyin.like(f'%{keyword}%'))
        ).all()
        results.extend([c.to_dict() for c in cities])
        
        # 搜索区县
        counties = self.session.query(County).join(City).filter(
            County.is_active == True,
            (County.name.like(f'%{keyword}%') | County.pinyin.like(f'%{keyword}%'))
        ).all()
        results.extend([c.to_dict() for c in counties])
        
        # 搜索镇
        towns = self.session.query(Town).join(County).filter(
            Town.is_active == True,
            (Town.name.like(f'%{keyword}%') | Town.pinyin.like(f'%{keyword}%'))
        ).all()
        results.extend([t.to_dict() for t in towns])
        
        # 搜索村
        villages = self.session.query(Village).join(Town).filter(
            Village.is_active == True,
            (Village.name.like(f'%{keyword}%') | Village.pinyin.like(f'%{keyword}%'))
        ).all()
        results.extend([v.to_dict() for v in villages])
        
        return results
    
    def get_full_hierarchy(self, village_id):
        """获取完整的行政区划层级"""
        village = self.session.query(Village).filter(Village.id == village_id).first()
        if not village:
            return None
        
        return {
            'village': village.to_dict(),
            'town': village.town.to_dict() if village.town else None,
            'county': village.county.to_dict() if village.county else None,
            'city': village.city.to_dict() if village.city else None,
            'province': village.province.to_dict() if village.province else None,
            'full_path': f"{village.province.name}{village.city.name}{village.county.name}{village.town.name}{village.name}",
            'full_code': f"{village.province.code}{village.city.code}{village.county.code}{village.town.code}{village.code}"
        }
    
    def close(self):
        """关闭数据库连接"""
        self.session.close()

if __name__ == "__main__":
    # 测试代码
    service = AdministrativeQueryService()
    
    print("=== 测试行政区划查询系统 ===")
    
    # 获取所有省份
    provinces = service.get_provinces()
    print(f"省份数量: {len(provinces)}")
    for province in provinces[:3]:  # 显示前3个
        print(f"  {province.name} ({province.code})")
    
    # 获取北京市的城市
    beijing_province = next((p for p in provinces if p.name == '北京市'), None)
    if beijing_province:
        cities = service.get_cities_by_province(beijing_province.id)
        print(f"\n北京市的城市数量: {len(cities)}")
        for city in cities:
            print(f"  {city.name} ({city.code})")
    
    # 搜索测试
    search_results = service.search_administrative_divisions("朝阳")
    print(f"\n搜索'朝阳'的结果数量: {len(search_results)}")
    for result in search_results[:5]:  # 显示前5个
        print(f"  {result['name']} ({result['level']})")
    
    service.close()