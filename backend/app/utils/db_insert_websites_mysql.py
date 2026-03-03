import os
from dotenv import load_dotenv
import re
import datetime
import pymysql
from pymysql.err import OperationalError, ProgrammingError

# -------------------------- 数据库配置（请修改为你的实际配置） --------------------------


# 加载环境变量
load_dotenv()

# 数据库连接配置
config = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'db': os.getenv('MYSQL_DB'),
    'charset': 'utf8mb4'
}

# -------------------------- 文件配置 --------------------------
WEBSITES_FILE = "websites.txt"  # 网站列表文件路径
TABLE_NAME = "websites"  # 数据库表名（和db_init_v2.py创建的表名一致）


# -------------------------- 域名提取函数（和原代码保持一致） --------------------------
def extract_domain(url):
    """提取URL的域名（复用app_recursive_debug.py中的逻辑）"""
    if not url:
        return ""
    # 移除http/https前缀
    url = re.sub(r'^https?://', '', url, flags=re.IGNORECASE)
    # 移除www.前缀
    url = re.sub(r'^www\.', '', url, flags=re.IGNORECASE)
    # 提取第一个/前的部分作为域名
    domain = url.split('/')[0] if '/' in url else url
    # 移除端口号
    domain = domain.split(':')[0] if ':' in domain else domain
    return domain


# -------------------------- 核心插入逻辑 --------------------------
def insert_websites_to_mysql():
    # 1. 校验文件是否存在
    if not os.path.exists(WEBSITES_FILE):
        print(f"❌ 错误：未找到文件 {WEBSITES_FILE}")
        return

    # 2. 读取并解析websites.txt
    website_list = []
    with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        # 跳过空行、注释行
        if not line or line.startswith('#'):
            continue

        parts = line.split('|')
        url = parts[0].strip()
        # 分类默认值为"新闻"，和原JSON初始化逻辑一致
        category = parts[1].strip() if len(parts) > 1 else '新闻'

        # 构造初始化数据（字段和原逻辑完全一致）
        website_data = {
            'url': url,
            'domain': extract_domain(url),
            'category': category,
            'status': '待抓取',
            'last_crawl': None,
            'total_pages': 0,
            'error': None,
            'progress': 0,
            'created_at': datetime.datetime.now().isoformat()
        }
        website_list.append(website_data)

    if not website_list:
        print("ℹ️ 未解析到有效网站数据（空行/注释行已跳过）")
        return

    # 3. 连接MySQL并处理数据
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        print("✅ 成功连接MySQL数据库")

        # 统计变量
        total_parsed = len(website_list)
        inserted_count = 0
        skipped_count = 0

        # 遍历解析后的网站，逐个校验+插入
        for website in website_list:
            url = website['url']

            # 第一步：校验URL是否已存在（核心去重逻辑）
            check_sql = f"SELECT 1 FROM {TABLE_NAME} WHERE url = %s LIMIT 1"
            cursor.execute(check_sql, (url,))
            exists = cursor.fetchone()

            if exists:
                # 已存在，忽略
                print(f"ℹ️ 网站 {url} 已存在，跳过")
                skipped_count += 1
                continue

            # 第二步：不存在，执行插入（字段和原初始化逻辑完全对齐）
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (
                url, domain, category, status, last_crawl, 
                total_pages, error, progress, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # 准备插入参数
            insert_params = (
                website['url'],
                website['domain'],
                website['category'],
                website['status'],
                website['last_crawl'],
                website['total_pages'],
                website['error'],
                website['progress'],
                website['created_at']
            )

            cursor.execute(insert_sql, insert_params)
            inserted_count += 1
            print(f"✅ 新增网站：{url}")

        # 提交事务
        conn.commit()
        print("\n" + "=" * 50)
        print(f"📊 处理完成：")
        print(f"   - 总共解析有效网站：{total_parsed} 条")
        print(f"   - 新增插入数据库：{inserted_count} 条")
        print(f"   - 已存在跳过：{skipped_count} 条")
        print("=" * 50)

    except OperationalError as e:
        print(f"❌ 数据库连接失败：{e}")
        if conn:
            conn.rollback()
    except ProgrammingError as e:
        print(f"❌ SQL执行错误（检查表名/字段名是否正确）：{e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        if conn:
            conn.rollback()
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("✅ 数据库连接已关闭")


if __name__ == "__main__":
    # 执行主逻辑
    insert_websites_to_mysql()