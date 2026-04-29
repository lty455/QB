"""
MySQL 到 SQLite 数据迁移脚本
功能：
1. 从 MySQL 读取数据（websites 和 crawl_file_record 表）
2. 创建 SQLite 数据库并初始化表结构
3. 导入所有数据
4. 验证数据完整性
"""

import pymysql
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ============= 配置 =============
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'db': os.getenv('MYSQL_DB', 'knowledge_graph'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'kg.db')
os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

# ============= SQLite 建表 SQL =============
SQLITE_TABLES = {
    'websites': """
    CREATE TABLE IF NOT EXISTS websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        domain TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT DEFAULT '待抓取' CHECK(status IN ('待抓取', '爬取中', '已完成', '失败')),
        last_crawl DATETIME NULL,
        total_pages INTEGER DEFAULT 0,
        error TEXT NULL,
        progress REAL DEFAULT 0.0,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """,
    'crawl_file_record': """
    CREATE TABLE IF NOT EXISTS crawl_file_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        page_num INTEGER DEFAULT 1,
        file_size INTEGER DEFAULT 0,
        crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_cleaned INTEGER DEFAULT 0,
        cleaned_time DATETIME NULL,
        FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
    )
    """
}

# ============= 日志颜色 =============
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(msg, color=Colors.BLUE):
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {msg}{Colors.END}")

def success(msg):
    log(msg, Colors.GREEN)

def warning(msg):
    log(msg, Colors.YELLOW)

def error(msg):
    log(msg, Colors.RED)


# ============= 迁移函数 =============
def test_mysql_connection():
    """测试 MySQL 连接"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        success(f"✓ MySQL 连接成功 (版本: {version['VERSION()']})")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        error(f"✗ MySQL 连接失败: {e}")
        return False


def create_sqlite_tables(sqlite_conn):
    """在 SQLite 中创建表"""
    cursor = sqlite_conn.cursor()
    try:
        for table_name, sql in SQLITE_TABLES.items():
            cursor.execute(sql)
            success(f"✓ 创建表: {table_name}")
        sqlite_conn.commit()
    except Exception as e:
        error(f"✗ 创建表失败: {e}")
        sqlite_conn.rollback()
        raise


def migrate_websites(mysql_conn, sqlite_conn):
    """迁移 websites 表"""
    mysql_cursor = mysql_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 读取 MySQL 中的数据
        mysql_cursor.execute("SELECT * FROM websites")
        rows = mysql_cursor.fetchall()
        
        log(f"从 MySQL 读取 {len(rows)} 条 websites 记录")
        
        # 插入到 SQLite
        for row in rows:
            sql = """
            INSERT INTO websites 
            (id, url, domain, category, status, last_crawl, total_pages, error, progress, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            sqlite_cursor.execute(sql, (
                row['id'],
                row['url'],
                row['domain'],
                row['category'],
                row['status'],
                row['last_crawl'].isoformat() if row['last_crawl'] else None,
                row['total_pages'],
                row['error'],
                row['progress'],
                row['is_active'],
                row['created_at'].isoformat() if row['created_at'] else None,
                row['updated_at'].isoformat() if row['updated_at'] else None,
            ))
        
        sqlite_conn.commit()
        success(f"✓ 成功导入 {len(rows)} 条 websites 记录")
        return len(rows)
        
    except Exception as e:
        error(f"✗ 迁移 websites 失败: {e}")
        sqlite_conn.rollback()
        raise
    finally:
        mysql_cursor.close()


def migrate_crawl_file_records(mysql_conn, sqlite_conn):
    """迁移 crawl_file_record 表"""
    mysql_cursor = mysql_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 读取 MySQL 中的数据
        mysql_cursor.execute("SELECT * FROM crawl_file_record")
        rows = mysql_cursor.fetchall()
        
        log(f"从 MySQL 读取 {len(rows)} 条 crawl_file_record 记录")
        
        # 插入到 SQLite
        for row in rows:
            sql = """
            INSERT INTO crawl_file_record
            (id, website_id, file_path, page_num, file_size, crawl_time, is_cleaned, cleaned_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            sqlite_cursor.execute(sql, (
                row['id'],
                row['website_id'],
                row['file_path'],
                row['page_num'],
                row['file_size'],
                row['crawl_time'].isoformat() if row['crawl_time'] else None,
                row['is_cleaned'],
                row['cleaned_time'].isoformat() if row['cleaned_time'] else None,
            ))
        
        sqlite_conn.commit()
        success(f"✓ 成功导入 {len(rows)} 条 crawl_file_record 记录")
        return len(rows)
        
    except Exception as e:
        error(f"✗ 迁移 crawl_file_record 失败: {e}")
        sqlite_conn.rollback()
        raise
    finally:
        mysql_cursor.close()


def verify_data(mysql_conn, sqlite_conn):
    """验证迁移的数据完整性"""
    success("\n🔍 开始数据验证...")
    
    mysql_cursor = mysql_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 验证 websites 表
        mysql_cursor.execute("SELECT COUNT(*) as cnt FROM websites")
        mysql_count = mysql_cursor.fetchone()['cnt']
        
        sqlite_cursor.execute("SELECT COUNT(*) as cnt FROM websites")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        if mysql_count == sqlite_count:
            success(f"✓ websites 表数据完整: {mysql_count} 条记录")
        else:
            warning(f"⚠ websites 表数据不匹配: MySQL {mysql_count} vs SQLite {sqlite_count}")
        
        # 验证 crawl_file_record 表
        mysql_cursor.execute("SELECT COUNT(*) as cnt FROM crawl_file_record")
        mysql_count = mysql_cursor.fetchone()['cnt']
        
        sqlite_cursor.execute("SELECT COUNT(*) as cnt FROM crawl_file_record")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        if mysql_count == sqlite_count:
            success(f"✓ crawl_file_record 表数据完整: {mysql_count} 条记录")
        else:
            warning(f"⚠ crawl_file_record 表数据不匹配: MySQL {mysql_count} vs SQLite {sqlite_count}")
        
        # 验证外键关系
        sqlite_cursor.execute("""
        SELECT COUNT(*) as invalid_count
        FROM crawl_file_record cfr
        WHERE NOT EXISTS (SELECT 1 FROM websites w WHERE w.id = cfr.website_id)
        """)
        invalid_count = sqlite_cursor.fetchone()[0]
        
        if invalid_count == 0:
            success(f"✓ 外键关系完整")
        else:
            warning(f"⚠ 发现 {invalid_count} 条孤立的文件记录")
        
        success("✓ 数据验证完成\n")
        
    except Exception as e:
        error(f"✗ 验证失败: {e}")
    finally:
        mysql_cursor.close()
        sqlite_cursor.close()


def main():
    """主迁移流程"""
    print("\n" + "="*60)
    print("🚀 MySQL 到 SQLite 数据迁移工具")
    print("="*60 + "\n")
    
    # 1. 测试 MySQL 连接
    if not test_mysql_connection():
        error("\n❌ 无法连接 MySQL，迁移中止")
        return False
    
    try:
        # 2. 连接到 MySQL 和 SQLite
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        sqlite_conn = sqlite3.connect(SQLITE_PATH)
        
        log(f"\n✓ SQLite 数据库路径: {SQLITE_PATH}")
        
        # 3. 在 SQLite 中创建表
        create_sqlite_tables(sqlite_conn)
        
        # 4. 迁移数据
        log("\n📊 开始迁移数据...")
        websites_count = migrate_websites(mysql_conn, sqlite_conn)
        crawl_file_count = migrate_crawl_file_records(mysql_conn, sqlite_conn)
        
        # 5. 验证数据
        verify_data(mysql_conn, sqlite_conn)
        
        # 6. 关闭连接
        mysql_conn.close()
        sqlite_conn.close()
        
        # 7. 总结
        print("="*60)
        success(f"✅ 迁移完成！")
        print(f"   - websites 表: {websites_count} 条记录")
        print(f"   - crawl_file_record 表: {crawl_file_count} 条记录")
        print(f"   - SQLite 数据库: {SQLITE_PATH}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        error(f"\n❌ 迁移过程出错: {e}")
        return False


if __name__ == '__main__':
    main()
