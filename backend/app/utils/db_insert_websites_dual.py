import os
import re
import datetime
import sqlite3
from dotenv import load_dotenv
import pymysql
from pymysql.err import OperationalError, ProgrammingError

# ======================== 环境变量和配置 ========================
load_dotenv()

# SQLite 配置（相对路径，便于迁移）
current_dir = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(current_dir, '..', '..', 'data', 'kg.db')

# MySQL 配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'db': os.getenv('MYSQL_DB'),
    'charset': 'utf8mb4'
}

# 公共配置
TABLE_NAME = "websites"
WEBSITES_FILE = "test.txt"


# ======================== 域名提取函数 ========================
def extract_domain(url):
    """提取URL的域名"""
    if not url:
        return ""
    url = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
    url = re.sub(r'^www\.', '', url, flags=re.IGNORECASE)
    domain = url.split('/')[0] if '/' in url else url
    domain = domain.split(':')[0] if ':' in domain else domain
    return domain


# ======================== MySQL 操作函数 ========================
class MySQLHandler:
    """MySQL 数据库处理器"""
    
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接 MySQL"""
        try:
            self.conn = pymysql.connect(**self.config)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ MySQL 连接失败：{e}")
            return False
    
    def check_exists(self, url):
        """检查 URL 是否已存在"""
        try:
            check_sql = f"SELECT 1 FROM {TABLE_NAME} WHERE url = %s LIMIT 1"
            self.cursor.execute(check_sql, (url,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ MySQL 查询失败：{e}")
            return None
    
    def insert(self, website_data):
        """插入网站数据"""
        try:
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (
                url, domain, category, status, last_crawl, 
                total_pages, error, progress, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_sql, (
                website_data['url'],
                website_data['domain'],
                website_data['category'],
                website_data['status'],
                website_data['last_crawl'],
                website_data['total_pages'],
                website_data['error'],
                website_data['progress'],
                website_data['created_at']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ MySQL 插入失败：{e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# ======================== SQLite 操作函数 ========================
class SQLiteHandler:
    """SQLite 数据库处理器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接 SQLite"""
        try:
            # 确保数据目录存在
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ SQLite 连接失败：{e}")
            return False
    
    def check_exists(self, url):
        """检查 URL 是否已存在"""
        try:
            check_sql = f"SELECT COUNT(*) as cnt FROM {TABLE_NAME} WHERE url = ?"
            cursor = self.conn.cursor()
            cursor.execute(check_sql, (url,))
            result = cursor.fetchone()
            count = result['cnt'] if result else 0
            return count > 0
        except Exception as e:
            print(f"❌ SQLite 查询失败：{e}")
            return None
    
    def insert(self, website_data):
        """插入网站数据"""
        try:
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (
                url, domain, category, status, last_crawl, 
                total_pages, error, progress, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.conn.cursor()
            cursor.execute(insert_sql, (
                website_data['url'],
                website_data['domain'],
                website_data['category'],
                website_data['status'],
                website_data['last_crawl'],
                website_data['total_pages'],
                website_data['error'],
                website_data['progress'],
                website_data['created_at']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ SQLite 插入失败：{e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# ======================== 双数据库插入主逻辑 ========================
def insert_websites_to_dual_dbs():
    # 1. 校验文件是否存在
    if not os.path.exists(WEBSITES_FILE):
        print(f"❌ 错误：未找到文件 {WEBSITES_FILE}")
        return

    # 2. 读取并解析 websites.txt
    website_list = []
    with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split('|')
        url = parts[0].strip()
        category = parts[1].strip() if len(parts) > 1 else '新闻'

        website_list.append({
            'url': url,
            'domain': extract_domain(url),
            'category': category,
            'status': '待抓取',
            'last_crawl': None,
            'total_pages': 0,
            'error': None,
            'progress': 0,
            'created_at': datetime.datetime.now().isoformat()
        })

    if not website_list:
        print("ℹ️ 未解析到有效网站数据（空行/注释行已跳过）")
        return

    # 3. 初始化数据库处理器
    active_dbs = {}
    
    # 尝试连接 MySQL
    mysql_handler = MySQLHandler(MYSQL_CONFIG)
    if mysql_handler.connect():
        active_dbs['MySQL'] = {'handler': mysql_handler, 'inserted': 0, 'skipped': 0}
        print("✅ 成功连接 MySQL 数据库")
    else:
        print("⚠️ MySQL 暂不可用，跳过")

    # 尝试连接 SQLite
    sqlite_handler = SQLiteHandler(SQLITE_DB)
    if sqlite_handler.connect():
        active_dbs['SQLite'] = {'handler': sqlite_handler, 'inserted': 0, 'skipped': 0}
        print(f"✅ 成功连接 SQLite 数据库: {SQLITE_DB}")
    else:
        print("⚠️ SQLite 暂不可用，跳过")

    if not active_dbs:
        print("❌ 致命错误：MySQL 和 SQLite 都无法连接，任务终止。")
        return

    # 4. 执行双数据库写入
    total_parsed = len(website_list)
    print(f"\n🚀 开始处理 {total_parsed} 条数据，将同步写入到 {list(active_dbs.keys())}...\n")

    for website in website_list:
        url = website['url']
        inserted_targets = []
        skipped_targets = []

        for db_name, db_info in active_dbs.items():
            handler = db_info['handler']
            
            # 检查是否存在
            exists = handler.check_exists(url)
            
            if exists is None:
                # 查询出错，跳过
                continue
            elif exists:
                # 已存在，跳过
                db_info['skipped'] += 1
                skipped_targets.append(db_name)
            else:
                # 不存在，插入
                if handler.insert(website):
                    db_info['inserted'] += 1
                    inserted_targets.append(db_name)

        # 输出结果
        if inserted_targets:
            print(f"✅ 新增: {url} -> {', '.join(inserted_targets)}")
        elif skipped_targets:
            print(f"ℹ️ 跳过: {url} -> 已在 {', '.join(skipped_targets)} 中存在")

    # 5. 关闭连接
    for db_name, db_info in active_dbs.items():
        db_info['handler'].close()

    # 6. 打印统计报表
    print("\n" + "=" * 60)
    print(f"📊 双数据库批量同步处理完成")
    print(f"   解析总数：{total_parsed} 条")
    print("-" * 60)
    for db_name, db_info in active_dbs.items():
        print(f"📂 {db_name} 库:")
        print(f"   ├─ 新增插入：{db_info['inserted']} 条")
        print(f"   └─ 已存在跳过：{db_info['skipped']} 条")
    print("=" * 60)


if __name__ == "__main__":
    insert_websites_to_dual_dbs()
