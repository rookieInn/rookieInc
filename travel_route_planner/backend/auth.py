"""
认证和安全模块
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from config.settings import settings
from database.database import get_db
from database.models import User
import logging

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# HTTP Bearer认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """验证令牌并返回用户名"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        username = verify_token(token)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def check_user_permissions(user: User, resource_user_id: int) -> bool:
    """检查用户权限"""
    # 用户可以访问自己的资源，管理员可以访问所有资源
    return user.id == resource_user_id or user.is_admin


def validate_input_data(data: dict, required_fields: list) -> bool:
    """验证输入数据"""
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True


def sanitize_input(text: str) -> str:
    """清理输入文本，防止XSS攻击"""
    if not text:
        return ""
    
    # 移除潜在的恶意字符
    dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'onclick', 'onload']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


def validate_travel_dates(start_date: str, end_date: str) -> bool:
    """验证旅行日期"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # 开始日期不能早于今天
        if start.date() < datetime.now().date():
            return False
        
        # 结束日期不能早于开始日期
        if end.date() < start.date():
            return False
        
        # 旅行时间不能超过30天
        if (end - start).days > 30:
            return False
        
        return True
        
    except ValueError:
        return False


def validate_budget(budget: Optional[float]) -> bool:
    """验证预算"""
    if budget is None:
        return True
    
    return budget > 0 and budget <= 1000000  # 最大100万


def validate_travel_type(travel_type: Optional[str]) -> bool:
    """验证旅行类型"""
    if travel_type is None:
        return True
    
    valid_types = [
        "亲子游", "蜜月游", "独自旅行", "朋友聚会", 
        "商务旅行", "休闲游", "探险游", "文化游"
    ]
    
    return travel_type in valid_types


def check_content_safety(content: str) -> bool:
    """检查内容安全性"""
    # 敏感词检测（简化版本）
    sensitive_words = [
        "暴力", "色情", "政治", "宗教", "赌博", "毒品",
        "自杀", "自残", "恐怖", "极端"
    ]
    
    content_lower = content.lower()
    for word in sensitive_words:
        if word in content_lower:
            return False
    
    return True


def generate_session_id() -> str:
    """生成会话ID"""
    import uuid
    return str(uuid.uuid4())


def log_security_event(event_type: str, user_id: Optional[int], details: str):
    """记录安全事件"""
    logger.warning(f"安全事件: {event_type}, 用户ID: {user_id}, 详情: {details}")


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.failed_login_attempts = {}  # 记录失败登录次数
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5分钟
    
    def check_login_attempts(self, username: str) -> bool:
        """检查登录尝试次数"""
        if username in self.failed_login_attempts:
            attempts, last_attempt = self.failed_login_attempts[username]
            if attempts >= self.max_failed_attempts:
                # 检查是否还在锁定期内
                if datetime.now().timestamp() - last_attempt < self.lockout_duration:
                    return False
                else:
                    # 锁定期已过，重置计数
                    del self.failed_login_attempts[username]
        
        return True
    
    def record_failed_login(self, username: str):
        """记录失败登录"""
        if username in self.failed_login_attempts:
            attempts, _ = self.failed_login_attempts[username]
            self.failed_login_attempts[username] = (attempts + 1, datetime.now().timestamp())
        else:
            self.failed_login_attempts[username] = (1, datetime.now().timestamp())
    
    def record_successful_login(self, username: str):
        """记录成功登录"""
        if username in self.failed_login_attempts:
            del self.failed_login_attempts[username]


# 创建全局安全管理器实例
security_manager = SecurityManager()