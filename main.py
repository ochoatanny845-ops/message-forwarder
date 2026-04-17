"""消息转发机器人 - 主程序"""
from telethon import TelegramClient, events
from telegram.ext import Application
import asyncio
from config import Config
from database import ForwardDatabase
from forwarder import forward_message
from parser import extract_product_name_from_button
from matcher import find_product

async def init():
    """初始化函数"""
    # 初始化
    print("🚀 消息转发机器人启动中...")

    # 验证配置
    if not Config.validate():
        exit(1)

    print("✅ 配置验证通过")

    # 初始化Telegram客户端
    client = TelegramClient('session', Config.API_ID, Config.API_HASH)
    
    # 使用Application获取异步Bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    await application.initialize()  # ← 初始化Application
    bot = application.bot
    
    return client, bot, application  # ← 返回application

# 异步初始化
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client, bot, application = loop.run_until_complete(init())  # ← 接收application

# 初始化数据库
db = ForwardDatabase()

print(f"📡 监听群组: {Config.SOURCE_CHAT_ID}")
print(f"📢 转发频道: {Config.TARGET_CHANNEL_ID}")
print(f"🤖 ShopBot: @{Config.SHOPBOT_USERNAME}")
print(f"💾 数据库: {Config.SHOPBOT_DB_PATH}")
print()

@client.on(events.NewMessage(chats=Config.SOURCE_CHAT_ID))
async def handler(event):
    """处理新消息"""
    message = event.message
    
    # 检查是否已转发
    if db.is_forwarded(message.id):
        return
    
    # 检查是否为订单消息
    if "用户购买商品" not in message.text:
        return
    
    # 检查是否有按钮
    if not message.reply_markup or not message.reply_markup.rows:
        return
    
    # 提取商品名称
    original_button = message.reply_markup.rows[0].buttons[0]
    product_name = extract_product_name_from_button(original_button.text)
    
    # 智能匹配ShopBot商品
    product_data = find_product(product_name, Config.SHOPBOT_DB_PATH)
    
    # 转发消息（传递client）
    success = await forward_message(bot, message, product_data, client=client)
    
    # 标记已转发
    if success:
        db.mark_forwarded(message.id)

async def main():
    """主函数"""
    # 启动客户端
    await client.start()
    
    print("✅ 机器人已启动，正在监听消息...")
    print("按 Ctrl+C 停止")
    print()
    
    # 保持运行
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\n👋 机器人已停止")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
