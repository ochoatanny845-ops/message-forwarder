import requests

token = "8675559004:AAEl0Wn7pEia7eQH-ToCIZW-U0uWqr1VI2A"
chat_id = "5991190607"

# 使用你提供的动态Emoji ID
text = '''<tg-emoji emoji-id="5458603043203327669">🛒</tg-emoji> 用户购买商品

<tg-emoji emoji-id="5330237710655306682">📱</tg-emoji> 用户ID: 784****69
<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji> 购买商品: 🇳🇬+234尼日利亚
<tg-emoji emoji-id="5231200819986047254">📊</tg-emoji> 购买数量: 1

<tg-emoji emoji-id="4972482444025398275">💰</tg-emoji> 商品单价: 1.20 USDT'''

# 添加按钮
reply_markup = {
    "inline_keyboard": [[
        {
            "text": "🇳🇬+234尼日利亚 当前库存: 100",
            "url": "https://t.me/TGaccbbbot?start=buy"
        }
    ]]
}

response = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }
)

if response.status_code == 200:
    print(f"OK - message_id: {response.json()['result']['message_id']}")
else:
    print(f"FAILED: {response.text}")
