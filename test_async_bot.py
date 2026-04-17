import asyncio
from telegram.ext import Application

async def test():
    token = "8675559004:AAEl0Wn7pEia7eQH-ToCIZW-U0uWqr1VI2A"
    chat_id = "5991190607"
    
    # 使用Application获取异步Bot
    application = Application.builder().token(token).build()
    bot = application.bot
    
    text = '<tg-emoji emoji-id="5458603043203327669">🛒</tg-emoji> 测试动态Emoji\n\n<tg-emoji emoji-id="5330237710655306682">👤</tg-emoji> 这是用Application.bot发送的\n<tg-emoji emoji-id="5217822164362739968">🗂</tg-emoji> 应该显示动态Emoji'
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML'
    )
    
    print("OK - Test message sent")
    
    # 关闭Application
    await application.shutdown()

asyncio.run(test())
