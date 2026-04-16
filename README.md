# Message Forwarder - 订单消息转发机器人

## 功能介绍

自动监听源群组的订单消息，并转发到目标频道。

**核心功能：**
- 🎯 实时监听订单消息
- 🤖 智能匹配ShopBot商品
- 💰 读取ShopBot数据库精准价格
- 🔗 按钮跳转到ShopBot购买页面
- 🚫 消息去重机制
- 📊 转发日志记录

## 转发效果

**源消息：**
```
🔔 用户购买商品

📱 用户 ID: 668****97
👑 购买商品: 🇺🇸 +1美国 ~2-5月
📊 购买数量: 1

💰 商品单价: 0.47 USDT

[🇺🇸 +1美国 ~2-5月 当前库存: 4244]
```

**转发消息（你的频道）：**
```
🔔 用户购买商品

📱 用户 ID: 668****97
👑 购买商品: 🇺🇸 +1美国 ~2-5月
📊 购买数量: 1

💰 商品单价: 1.20 USDT  ← ShopBot数据库价格

[🇺🇸 +1美国 ~2-5月 当前库存: 4244]
↑ 点击跳转到ShopBot购买页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写配置：

```env
# Telegram API
API_ID=你的API_ID
API_HASH=你的API_HASH

# Bot Token
BOT_TOKEN=你的Bot_Token

# 源群组和目标频道
SOURCE_CHAT_ID=-1001234567890
TARGET_CHANNEL_ID=-1009876543210

# ShopBot配置
SHOPBOT_USERNAME=YourShopBot
SHOPBOT_DB_PATH=E:/工具/shop/shopbot/shopbot-stable/shopbot.db
```

### 3. 登录Telegram账户

首次运行需要登录你的Telegram账户：

```bash
python main.py
```

输入手机号和验证码完成登录。

### 4. 后台运行

```bash
# Windows
python main.py

# Linux (使用screen或tmux)
screen -S forwarder
python main.py
```

## 工作原理

### 智能匹配逻辑

1. **提取商品信息**
   - 从按钮文字提取商品名称
   - 例如：`🇺🇸 +1美国 ~2-5月`

2. **模糊匹配ShopBot商品**
   - 提取国家Emoji（🇺🇸）
   - 提取国家代码（+1）
   - 提取关键词（美国、2-5月）
   - 在ShopBot数据库中模糊匹配

3. **获取精准价格和库存**
   ```sql
   SELECT id, name, price, stock 
   FROM products 
   WHERE name LIKE '%🇺🇸%' 
     AND name LIKE '%+1%' 
     AND name LIKE '%美国%'
   LIMIT 1
   ```

4. **生成新按钮**
   - 按钮文字：完全复制原按钮
   - 按钮链接：`https://t.me/你的Bot?start=buy_{product_id}`

### 降级策略

**如果匹配失败（约15%概率）：**
- 价格：原价 + 0.2 USDT
- 按钮链接：`https://t.me/你的Bot?start=shop`（跳转到主菜单）

## 文件说明

```
message-forwarder/
├── main.py                 # 主程序入口
├── config.py               # 配置管理
├── forwarder.py            # 转发核心逻辑
├── matcher.py              # 商品智能匹配
├── parser.py               # 消息解析
├── database.py             # 去重数据库
├── .env                    # 环境变量（需创建）
├── .env.example            # 配置示例
├── .gitignore              # Git忽略文件
├── requirements.txt        # Python依赖
├── forwarded.db            # 已转发消息记录
├── session.session         # Telegram会话文件
└── README.md               # 本文档
```

## 配置说明

### 获取源群组ID

1. 将 @RawDataBot 添加到源群组
2. 发送任意消息
3. Bot会返回群组ID（-100开头的数字）

### 获取目标频道ID

1. 将 @RawDataBot 添加到目标频道
2. 发送任意消息
3. Bot会返回频道ID（-100开头的数字）

### 配置ShopBot数据库路径

指向你的ShopBot的 `shopbot.db` 文件路径，例如：
```
E:/工具/shop/shopbot/shopbot-stable/shopbot.db
```

## 日志和监控

**转发成功：**
```
✅ [23:50:12] 已转发: 🇺🇸 +1美国 ~2-5月
   价格: 0.47 → 1.20 USDT
   按钮: buy_8
```

**匹配失败（降级）：**
```
⚠️ [23:50:15] 未匹配: 🇯🇵 +81日本 ~新商品
   降级: 原价 + 0.2
   按钮: shop
```

**转发失败：**
```
❌ [23:50:18] 转发失败: 权限不足
   群组: -1001234567890
```

## 常见问题

### 1. 转发失败：权限不足

**解决：**
- 确保Bot是目标频道的管理员
- 确保Bot有发送消息权限

### 2. 商品匹配失败率高

**解决：**
- 检查ShopBot数据库商品名格式
- 调整 `matcher.py` 中的匹配逻辑
- 查看日志中的匹配失败原因

### 3. Session过期

**解决：**
- 删除 `session.session` 文件
- 重新运行 `python main.py`
- 重新登录Telegram账户

## 安全建议

- ⚠️ 不要泄露 `.env` 文件
- ⚠️ 定期检查转发日志
- ⚠️ 监控商品匹配准确率
- ⚠️ 定期备份 `forwarded.db`

## 维护

**定期检查：**
- 转发成功率（应 >95%）
- 商品匹配率（应 >85%）
- 价格一致性（抽查）

**更新商品映射：**
- ShopBot新增商品会自动支持
- 无需手动维护映射表

## 许可证

MIT License

## 作者

海棠 @ OpenClaw

## 更新日志

### v1.0.0 (2026-04-16)
- ✅ 初始版本
- ✅ 智能商品匹配
- ✅ 读取ShopBot数据库价格
- ✅ 消息去重机制
- ✅ 降级策略
