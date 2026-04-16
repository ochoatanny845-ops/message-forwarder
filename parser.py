"""消息解析模块"""
import re

def parse_order_message(text):
    """
    解析订单消息
    
    Args:
        text: 消息文本
    
    Returns:
        dict: 订单信息，如果不是订单消息则返回None
    """
    # 检查是否为订单消息
    if "用户购买商品" not in text:
        return None
    
    # 提取用户ID
    user_id_match = re.search(r'用户\s*ID[：:]\s*(\d+\*+\d+)', text)
    user_id = user_id_match.group(1) if user_id_match else "未知"
    
    # 提取商品名称
    product_match = re.search(r'购买商品[：:]\s*(.+?)(?:\n|$)', text)
    product_name = product_match.group(1).strip() if product_match else None
    
    # 提取购买数量
    quantity_match = re.search(r'购买数量[：:]\s*(\d+)', text)
    quantity = quantity_match.group(1) if quantity_match else "1"
    
    # 提取商品单价
    price_match = re.search(r'商品单价[：:]\s*([\d.]+)\s*USDT', text)
    price = float(price_match.group(1)) if price_match else 0.0
    
    if not product_name:
        return None
    
    return {
        'user_id': user_id,
        'product_name': product_name,
        'quantity': quantity,
        'price': price
    }

def extract_product_name_from_button(button_text):
    """
    从按钮文字中提取商品名称
    
    Args:
        button_text: 按钮文字，如 "🇺🇸 +1美国 ~2-5月 当前库存: 4244"
    
    Returns:
        str: 商品名称，如 "🇺🇸 +1美国 ~2-5月"
    """
    # 移除库存信息
    match = re.match(r'(.+?)\s*当前库存[：:]\s*\d+', button_text)
    if match:
        return match.group(1).strip()
    
    return button_text.strip()
