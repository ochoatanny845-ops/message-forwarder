"""配置管理模块"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # Telegram API
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', '')
    
    # Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # 源群组和目标频道
    SOURCE_CHAT_ID = int(os.getenv('SOURCE_CHAT_ID', '0'))
    TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', '0'))
    
    # ShopBot配置
    SHOPBOT_USERNAME = os.getenv('SHOPBOT_USERNAME', '')
    SHOPBOT_DB_PATH = os.getenv('SHOPBOT_DB_PATH', '')
    
    # 降级策略
    FALLBACK_PRICE_INCREASE = float(os.getenv('FALLBACK_PRICE_INCREASE', '0.2'))
    
    @classmethod
    def validate(cls):
        """验证配置"""
        errors = []
        
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID未配置")
        
        if not cls.API_HASH:
            errors.append("API_HASH未配置")
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN未配置")
        
        if not cls.SOURCE_CHAT_ID or cls.SOURCE_CHAT_ID == 0:
            errors.append("SOURCE_CHAT_ID未配置")
        
        if not cls.TARGET_CHANNEL_ID or cls.TARGET_CHANNEL_ID == 0:
            errors.append("TARGET_CHANNEL_ID未配置")
        
        if not cls.SHOPBOT_USERNAME:
            errors.append("SHOPBOT_USERNAME未配置")
        
        if not cls.SHOPBOT_DB_PATH:
            errors.append("SHOPBOT_DB_PATH未配置")
        
        if errors:
            print("❌ 配置错误：")
            for error in errors:
                print(f"   - {error}")
            print("\n请检查 .env 文件配置")
            return False
        
        return True
