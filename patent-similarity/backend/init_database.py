"""
数据库初始化脚本 - 只在第一次部署时运行
"""
import asyncio
import sys
from app.db.database import init_db, create_tables, close_db
from app.core.logging import configure_logging, get_logger

configure_logging("INFO")
logger = get_logger(__name__)


async def init_database():
    """初始化数据库 - 创建所有表"""
    try:
        logger.info("Starting database initialization...")
        
        # 初始化数据库连接
        init_db()
        logger.info("Database connection initialized")
        
        # 创建所有表
        await create_tables()
        logger.info("Database tables created successfully")
        
        logger.info("Database initialization completed!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        await close_db()


if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)
