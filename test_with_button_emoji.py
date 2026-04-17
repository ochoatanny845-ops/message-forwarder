import asyncio
from telegram.ext import Application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def test():
    token = "8675559004:AAEl0Wn7pEia7eQH-ToCIZW-U0uWqr1VI2A"
    chat_id = "5991190607"
    
    # 使用Application获取异步Bot
    application = Application.builder().token(token).build()
    await application.initialize()
    bot = application.bot
    
    text = '<tg-emoji emoji-id="5458603043203327669">🛒</tg-emoji> 测试动态Emoji + 按钮\n\n<tg-emoji emoji-id="5330237710655306682">👤</tg-emoji> 带按钮的消息\n<tg-emoji emoji-id="5217822164362739968">🗂</tg-emoji> 商品测试'
    
    # 添加按钮
    button = InlineKeyboardButton(
        "🇨🇳 测试按钮",
        url="https://t.me/TGaccbbbot?start=test"
    )
    keyboard = InlineKeyboardMarkup([[button]])
    
    # 带按钮发送
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML',
        reply_markup=keyboard  # ← 带按钮
    )
    
    print("OK - Test with button sent")
    
    # 关闭Application
    await application.shutdown()

asyncio.run(test())
