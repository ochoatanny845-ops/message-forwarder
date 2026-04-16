"""消息去重数据库模块"""
import sqlite3
import os

class ForwardDatabase:
    """消息去重数据库"""
    
    def __init__(self, db_path='forwarded.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS forwarded_messages (
                message_id INTEGER PRIMARY KEY,
                forwarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_forwarded(self, message_id):
        """检查消息是否已转发"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT 1 FROM forwarded_messages WHERE message_id = ?', (message_id,))
        result = c.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_forwarded(self, message_id):
        """标记消息已转发"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('INSERT OR IGNORE INTO forwarded_messages (message_id) VALUES (?)', (message_id,))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_records(self, days=30):
        """清理旧记录"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            'DELETE FROM forwarded_messages WHERE forwarded_at < datetime("now", "-? days")',
            (days,)
        )
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        return deleted
