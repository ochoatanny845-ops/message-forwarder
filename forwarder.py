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
    
    # ⚠️ Telegram的offset/length是按UTF-16编码计算的
    # 需要将文本转换为UTF-16来正确处理
    text_utf16 = text.encode('utf-16-le')
    
    result = ""
    last_offset = 0
    
    # 按offset排序
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    
    for entity in sorted_entities:
        # UTF-16偏移量（每个单位2字节）
        start_byte = entity.offset * 2
        end_byte = (entity.offset + entity.length) * 2
        
        # 提取前面的普通文本
        plain_bytes = text_utf16[last_offset * 2:start_byte]
        plain_text = plain_bytes.decode('utf-16-le', errors='ignore')
        result += plain_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 提取实体对应的文本
        entity_bytes = text_utf16[start_byte:end_byte]
        entity_text = entity_bytes.decode('utf-16-le', errors='ignore')
        
        # 处理动态Emoji
        if isinstance(entity, MessageEntityCustomEmoji):
            result += f'<tg-emoji emoji-id="{entity.document_id}">{entity_text}</tg-emoji>'
        else:
            # 其他实体保持原样（也需要转义）
            result += entity_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        last_offset = entity.offset + entity.length
    
    # 添加剩余文本（转义HTML字符）
    remaining_bytes = text_utf16[last_offset * 2:]
    remaining_text = remaining_bytes.decode('utf-16-le', errors='ignore')
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
        # ✅ 始终使用源价格 + 0.2
        new_price = order_data['price'] + 0.2
        
        if product_data:
            # 匹配成功 - 使用ShopBot商品ID
            button_url = f"https://t.me/{Config.SHOPBOT_USERNAME}?start=buy_{product_data['id']}"
            match_status = f"✅ 匹配成功 (ID: {product_data['id']}，价格: {order_data['price']:.2f} + 0.2 = {new_price:.2f})"
        else:
            # 匹配失败 - 降级到主菜单
            button_url = f"https://t.me/{Config.SHOPBOT_USERNAME}?start=shop"
            match_status = f"⚠️  匹配失败，降级到主菜单（价格: {order_data['price']:.2f} + 0.2 = {new_price:.2f}）"
        
        # ✅ 先转换entities为HTML（保留动态Emoji）
        message_html = entities_to_html(message.text, message.entities)
        
        # 🐛 调试：打印HTML内容
        print(f"   📋 原始文本前100字符: {message.text[:100]}")
        print(f"   📋 HTML文本前200字符: {message_html[:200]}")
        if message.entities:
            print(f"   📋 Entities数量: {len(message.entities)}")
            for i, e in enumerate(message.entities[:3]):  # 只打印前3个
                print(f"      {i+1}. {type(e).__name__} offset={e.offset} len={e.length}")
                if isinstance(e, MessageEntityCustomEmoji):
                    print(f"         → document_id={e.document_id}")
        
        # ✅ 再替换价格（在HTML文本中替换）
        message_html = re.sub(
            r'(商品单价[：:]\s*)[\d.]+(\s*USDT)',
            rf'\g<1>{new_price:.2f}\g<2>',
            message_html
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
