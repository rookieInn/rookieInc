"""
数据库迁移脚本：为User表添加session_token和last_login_at字段
"""
from sqlalchemy import create_engine, text
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """升级数据库结构"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # 添加session_token字段
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN session_token VARCHAR(500) NULL,
                ADD INDEX idx_users_session_token (session_token)
            """))
            
            # 添加last_login_at字段
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN last_login_at DATETIME NULL
            """))
            
            conn.commit()
            logger.info("成功添加session_token和last_login_at字段到users表")
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            conn.rollback()
            raise

def downgrade():
    """回滚数据库结构"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # 删除添加的字段
            conn.execute(text("""
                ALTER TABLE users 
                DROP COLUMN session_token,
                DROP COLUMN last_login_at
            """))
            
            conn.commit()
            logger.info("成功删除session_token和last_login_at字段")
            
        except Exception as e:
            logger.error(f"数据库回滚失败: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()