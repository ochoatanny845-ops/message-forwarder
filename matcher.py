"""商品智能匹配模块"""
import sqlite3
import re

def find_product(product_name, db_path):
    """
    从ShopBot数据库中智能匹配商品
    
    Args:
        product_name: 商品名称，如 "🇺🇸 +1美国 ~2-5月"
        db_path: ShopBot数据库路径
    
    Returns:
        dict: 商品信息 {'id': int, 'name': str, 'price': float, 'stock': int}
        None: 匹配失败
    """
    try:
        # 提取国家Emoji
        emoji_match = re.search(r'[\U0001F1E6-\U0001F1FF]{2}', product_name)
        country_emoji = emoji_match.group(0) if emoji_match else None
        
        # 提取国家代码
        code_match = re.search(r'\+\d+', product_name)
        country_code = code_match.group(0) if code_match else None
        
        # 提取关键词（去除Emoji和特殊符号）
        keywords = re.sub(r'[\U0001F1E6-\U0001F1FF\+\~\-\*]', ' ', product_name)
        keywords = [k.strip() for k in keywords.split() if k.strip() and len(k.strip()) > 1]
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 构建查询
        query = "SELECT id, name, price, stock FROM products WHERE 1=1"
        params = []
        
        # 添加国家Emoji条件
        if country_emoji:
            query += " AND name LIKE ?"
            params.append(f"%{country_emoji}%")
        
        # 添加国家代码条件
        if country_code:
            query += " AND name LIKE ?"
            params.append(f"%{country_code}%")
        
        # 添加关键词条件（至少匹配一个）
        if keywords:
            keyword_conditions = " OR ".join(["name LIKE ?" for _ in keywords])
            query += f" AND ({keyword_conditions})"
            params.extend([f"%{k}%" for k in keywords])
        
        query += " LIMIT 1"
        
        # 执行查询
        c.execute(query, params)
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'price': result[2],
                'stock': result[3]
            }
        
        return None
    
    except Exception as e:
        print(f"❌ 商品匹配失败: {e}")
        return None
