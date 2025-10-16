"""
测试JWT单点登录逻辑（不依赖服务器）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from jose import jwt
import uuid

# 模拟配置
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, session_id: str = None):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加session_id用于单点登录控制
    if session_id:
        to_encode.update({"session_id": session_id})
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # 签发时间
        "jti": str(uuid.uuid4())   # JWT ID，用于唯一标识token
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌并返回payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        print(f"Token验证失败: {e}")
        return None

def test_jwt_single_session():
    """测试JWT单点登录逻辑"""
    print("=== JWT单点登录逻辑测试 ===\n")
    
    username = "testuser"
    
    # 1. 第一次登录
    print("1. 第一次登录...")
    session_id_1 = str(uuid.uuid4())
    token1 = create_access_token(
        data={"sub": username}, 
        session_id=session_id_1
    )
    print(f"✓ 生成token1: {token1[:50]}...")
    print(f"  session_id: {session_id_1}")
    
    # 2. 验证第一个token
    print("\n2. 验证第一个token...")
    payload1 = verify_token(token1)
    if payload1:
        print(f"✓ Token1验证成功")
        print(f"  用户名: {payload1.get('sub')}")
        print(f"  session_id: {payload1.get('session_id')}")
        print(f"  JWT ID: {payload1.get('jti')}")
    else:
        print("✗ Token1验证失败")
        return
    
    # 3. 第二次登录（模拟挤掉第一次登录）
    print("\n3. 第二次登录（模拟挤掉第一次登录）...")
    session_id_2 = str(uuid.uuid4())
    token2 = create_access_token(
        data={"sub": username}, 
        session_id=session_id_2
    )
    print(f"✓ 生成token2: {token2[:50]}...")
    print(f"  session_id: {session_id_2}")
    
    # 4. 验证第二个token
    print("\n4. 验证第二个token...")
    payload2 = verify_token(token2)
    if payload2:
        print(f"✓ Token2验证成功")
        print(f"  用户名: {payload2.get('sub')}")
        print(f"  session_id: {payload2.get('session_id')}")
        print(f"  JWT ID: {payload2.get('jti')}")
    else:
        print("✗ Token2验证失败")
        return
    
    # 5. 模拟服务端session验证
    print("\n5. 模拟服务端session验证...")
    
    # 模拟用户当前有效的session_token（第二次登录后的）
    current_session_token = token2
    
    print(f"当前有效session_token: {current_session_token[:50]}...")
    
    # 验证token1（应该失效）
    print(f"\n验证token1（应该失效）:")
    if token1 == current_session_token:
        print("✓ Token1仍然有效")
    else:
        print("✓ Token1已失效（符合预期）")
    
    # 验证token2（应该有效）
    print(f"\n验证token2（应该有效）:")
    if token2 == current_session_token:
        print("✓ Token2仍然有效（符合预期）")
    else:
        print("✗ Token2已失效（不符合预期）")
    
    # 6. 测试token过期
    print("\n6. 测试token过期...")
    
    # 创建一个已过期的token
    expired_data = {"sub": username}
    expired_data.update({
        "exp": datetime.utcnow() - timedelta(minutes=1),  # 1分钟前过期
        "iat": datetime.utcnow() - timedelta(minutes=2),
        "jti": str(uuid.uuid4())
    })
    expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"过期token: {expired_token[:50]}...")
    expired_payload = verify_token(expired_token)
    if expired_payload is None:
        print("✓ 过期token验证失败（符合预期）")
    else:
        print("✗ 过期token仍然有效（不符合预期）")
    
    # 7. 测试无效token
    print("\n7. 测试无效token...")
    invalid_token = "invalid.token.here"
    invalid_payload = verify_token(invalid_token)
    if invalid_payload is None:
        print("✓ 无效token验证失败（符合预期）")
    else:
        print("✗ 无效token验证成功（不符合预期）")
    
    print("\n=== 测试完成 ===")

def test_session_management():
    """测试会话管理逻辑"""
    print("\n=== 会话管理逻辑测试 ===\n")
    
    # 模拟用户数据
    class MockUser:
        def __init__(self, username, session_token=None):
            self.username = username
            self.session_token = session_token
            self.last_login_at = None
    
    user = MockUser("testuser")
    
    # 1. 第一次登录
    print("1. 第一次登录...")
    session_id_1 = str(uuid.uuid4())
    token1 = create_access_token({"sub": user.username}, session_id_1)
    user.session_token = token1
    user.last_login_at = datetime.utcnow()
    print(f"✓ 用户登录，session_token: {token1[:30]}...")
    
    # 2. 验证当前会话
    print("\n2. 验证当前会话...")
    def validate_session(token, user):
        if user.session_token != token:
            return False, "登录已失效，请重新登录"
        
        payload = verify_token(token)
        if not payload:
            return False, "Token无效"
        
        return True, "会话有效"
    
    valid, message = validate_session(token1, user)
    print(f"Token1验证: {message}")
    
    # 3. 第二次登录（挤掉第一次）
    print("\n3. 第二次登录（挤掉第一次）...")
    session_id_2 = str(uuid.uuid4())
    token2 = create_access_token({"sub": user.username}, session_id_2)
    user.session_token = token2  # 更新session_token
    user.last_login_at = datetime.utcnow()
    print(f"✓ 用户重新登录，新session_token: {token2[:30]}...")
    
    # 4. 验证旧token失效
    print("\n4. 验证旧token失效...")
    valid, message = validate_session(token1, user)
    print(f"Token1验证: {message}")
    
    # 5. 验证新token有效
    print("\n5. 验证新token有效...")
    valid, message = validate_session(token2, user)
    print(f"Token2验证: {message}")
    
    # 6. 登出
    print("\n6. 登出...")
    user.session_token = None
    print("✓ 用户登出，session_token已清除")
    
    # 7. 验证登出后token失效
    print("\n7. 验证登出后token失效...")
    valid, message = validate_session(token2, user)
    print(f"Token2验证: {message}")
    
    print("\n=== 会话管理测试完成 ===")

if __name__ == "__main__":
    print(f"开始JWT单点登录逻辑测试 - {datetime.now()}")
    print("=" * 60)
    
    # 基础JWT逻辑测试
    test_jwt_single_session()
    
    # 会话管理测试
    test_session_management()
    
    print(f"\n所有测试完成 - {datetime.now()}")