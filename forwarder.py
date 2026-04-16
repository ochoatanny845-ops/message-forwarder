"""消息转发核心逻辑模块"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telethon.tl.types import MessageEntityCustomEmoji
from parser import parse_order_message, extract_product_name_from_button
from matcher import find_product
from config import Config
from datetime import datetime
import re

def entities_to_html(text, entities):
    """
    将Telethon的entities转换为HTML格式（支持动态Emoji）
    
    Args:
        text: 消息文本
        entities: Telethon的MessageEntity列表
    
    Returns:
        str: HTML格式的文本
    """
    if not entities:
        return text
    
    result = ""
    last_offset = 0
    
    # 按offset排序
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    
    for entity in sorted_entities:
        # 添加前面的普通文本（转义HTML字符）
        plain_text = text[last_offset:entity.offset]
        result += plain_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 提取实体对应的文本
        entity_text = text[entity.offset:entity.offset + entity.length]
        
        # 处理动态Emoji
        if isinstance(entity, MessageEntityCustomEmoji):
            result += f'<tg-emoji emoji-id="{entity.document_id}">{entity_text}</tg-emoji>'
        else:
            # 其他实体保持原样（也需要转义）
            result += entity_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        last_offset = entity.offset + entity.length
    
    # 添加剩余文本（转义HTML字符）
    remaining_text = text[last_offset:]
    result += remaining_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    return result


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
        
        # 转换entities为HTML（保留动态Emoji）
        message_html = entities_to_html(message_text, message.entities)
        
        # 构造新按钮（文字完全复制，链接修改）
        new_button = InlineKeyboardButton(
            original_button.text,  # 按钮文字完全一样
            url=button_url  # 链接改成ShopBot
        )
        
        keyboard = InlineKeyboardMarkup([[new_button]])
        
        # 发送到目标频道
        await bot.send_message(
            chat_id=Config.TARGET_CHANNEL_ID,
            text=message_html,  # 使用HTML格式
            parse_mode='HTML',  # 支持动态Emoji
            reply_markup=keyboard
        )
        
        # 记录日志
        timestamp = datetime.now().strftime("%H:%M:%S")
        has_custom_emoji = any(isinstance(e, MessageEntityCustomEmoji) for e in (message.entities or []))
        emoji_status = "✨ 动态Emoji" if has_custom_emoji else "📝 普通文本"
        print(f"✅ [{timestamp}] 已转发: {order_data['product_name']} ({emoji_status})")
        print(f"   价格: {order_data['price']:.2f} → {new_price:.2f} USDT")
        print(f"   {match_status}")
        
        return True
    
    except Exception as e:
        print(f"❌ 转发失败: {e}")
        return False
