import requests

token = "8675559004:AAEl0Wn7pEia7eQH-ToCIZW-U0uWqr1VI2A"
chat_id = "5991190607"

text = '''<tg-emoji emoji-id="5458603043203327669">🛒</tg-emoji> 测试动态Emoji

<tg-emoji emoji-id="5330237710655306682">📱</tg-emoji> 这是使用新Bot发送的消息
<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji> 支持动态Emoji
<tg-emoji emoji-id="5231200819986047254">📊</tg-emoji> Bot Token: 8675559004
<tg-emoji emoji-id="4972482444025398275">💰</tg-emoji> 测试成功！'''

response = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
)

if response.status_code == 200:
    print(f"OK - message_id: {response.json()['result']['message_id']}")
else:
    print(f"FAILED: {response.text}")
