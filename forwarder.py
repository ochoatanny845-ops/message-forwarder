"""消息转发核心逻辑模块"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from parser import parse_order_message, extract_product_name_from_button
from matcher import find_product
from config import Config
from datetime import datetime

async def forward_message(bot, message, product_data=None):
    """
    转发订单消息到目标频道
    
    Args:
        bot: Telegram Bot实例
        message: 原始消息对象
        product_data: 匹配的商品数据（可选）
    
    Returns:
        bool: 转发是否成功
    """
    try:
        # 解析消息
        order_data = parse_order_message(message.text)
        if not order_data:
            print("⚠️  不是订单消息，跳过")
            return False
        
        # 获取原始按钮
        original_button = None
        if message.reply_markup and message.reply_markup.rows:
            original_button = message.reply_markup.rows[0].buttons[0]
        
        if not original_button:
            print("⚠️  消息没有按钮，跳过")
            return False
        
        # 确定价格和按钮
        if product_data:
            # 匹配成功 - 使用ShopBot数据库价格
            new_price = product_data['price']
            button_url = f"https://t.me/{Config.SHOPBOT_USERNAME}?start=buy_{product_data['id']}"
            match_status = f"✅ 匹配成功 (ID: {product_data['id']})"
        else:
            # 匹配失败 - 降级策略
            new_price = order_data['price'] + Config.FALLBACK_PRICE_INCREASE
            button_url = f"https://t.me/{Config.SHOPBOT_USERNAME}?start=shop"
            match_status = f"⚠️  匹配失败，降级 (+{Config.FALLBACK_PRICE_INCREASE})"
        
        # 直接复制原始消息文本，只替换价格
        import re
        message_text = re.sub(
            r'(商品单价[：:]\s*)[\d.]+(\s*USDT)',
            rf'\g<1>{new_price:.2f}\g<2>',
            message.text  # 保留原始格式（包括动态Emoji）
        )
        
        # 构造新按钮（文字完全复制，链接修改）
        new_button = InlineKeyboardButton(
            original_button.text,  # 按钮文字完全一样
            url=button_url  # 链接改成ShopBot
        )
        
        keyboard = InlineKeyboardMarkup([[new_button]])
        
        # 发送到目标频道
        await bot.send_message(
            chat_id=Config.TARGET_CHANNEL_ID,
            text=message_text,
            parse_mode='HTML',  # 支持动态Emoji
            reply_markup=keyboard
        )
        
        # 记录日志
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"✅ [{timestamp}] 已转发: {order_data['product_name']}")
        print(f"   价格: {order_data['price']:.2f} → {new_price:.2f} USDT")
        print(f"   {match_status}")
        
        return True
    
    except Exception as e:
        print(f"❌ 转发失败: {e}")
        return False
