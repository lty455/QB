import os
from dotenv import load_dotenv
import pymysql
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CRAWL_DATA_DIR = os.path.join(DATA_DIR, 'websites')

# ========== 数据库配置 ==========
# 数据库类型: 'auto' | 'mysql' | 'sqlite'
# 'auto': 自动模式，优先使用 MySQL，MySQL 失败则自动切换到 SQLite（推荐）
# 'mysql': 强制使用 MySQL
# 'sqlite': 强制使用 SQLite
DB_TYPE = os.getenv('DB_TYPE', 'auto')

# MySQL 配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'db': os.getenv('MYSQL_DB', 'knowledge_graph'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# SQLite 配置
SQLITE_PATH = os.path.join(DATA_DIR, 'kg.db')

# 默认请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}