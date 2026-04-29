import os
import re
import datetime
import sqlite3

# ======================== SQLite 数据库配置 ========================
# 使用相对于脚本的相对路径，便于项目迁移
# 脚本位置: backend/app/utils/db_insert_websites_sqlite.py
# 数据库位置: backend/data/kg.db
# 相对路径: ../../data/kg.db
current_dir = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(current_dir, '..', '..', 'data', 'kg.db')
TABLE_NAME = "websites"
WEBSITES_FILE = "test.txt"  # 网站列表文件路径


# ======================== 域名提取函数 ========================
def extract_domain(url):
    """提取URL的域名"""
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


# ======================== SQLite 插入逻辑 ========================
def insert_websites_to_sqlite():
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
        # 跳过空行、注释行
        if not line or line.startswith('#'):
            continue

        parts = line.split('|')
        url = parts[0].strip()
        # 分类默认值为"新闻"
        category = parts[1].strip() if len(parts) > 1 else '新闻'

        # 构造初始化数据
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

    # 3. 连接 SQLite 并处理数据
    conn = None
    try:
        # 确保数据目录存在
        db_dir = os.path.dirname(SQLITE_DB)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ 创建数据目录: {db_dir}")

        # 连接 SQLite 数据库
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row  # 允许按列名访问
        cursor = conn.cursor()
        print(f"✅ 成功连接 SQLite 数据库: {SQLITE_DB}")

        # 统计变量
        total_parsed = len(website_list)
        inserted_count = 0
        skipped_count = 0

        # 遍历解析后的网站，逐个校验+插入
        for website in website_list:
            url = website['url']

            # 第一步：校验 URL 是否已存在（核心去重逻辑）
            # ⚠️ 关键修复：使用 ? 占位符而不是 %s（SQLite 标准）
            check_sql = f"SELECT COUNT(*) as cnt FROM {TABLE_NAME} WHERE url = ?"
            cursor.execute(check_sql, (url,))
            result = cursor.fetchone()
            
            # 获取计数（兼容 sqlite3.Row 对象）
            count = result['cnt'] if result else 0
            
            if count > 0:
                # 已存在，忽略
                print(f"ℹ️ 网站 {url} 已存在，跳过")
                skipped_count += 1
                continue

            # 第二步：不存在，执行插入
            # ⚠️ 关键修复：所有占位符都用 ? （SQLite 标准）
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (
                url, domain, category, status, last_crawl, 
                total_pages, error, progress, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        print(f"   - 数据库位置：{SQLITE_DB}")
        print("=" * 50)

    except sqlite3.OperationalError as e:
        print(f"❌ SQLite 操作错误（检查表名/字段名/数据库是否存在）：{e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        if conn:
            conn.rollback()
    finally:
        # 关闭连接
        if conn:
            conn.close()
        print("✅ SQLite 数据库连接已关闭")


if __name__ == "__main__":
    # 执行主逻辑
    insert_websites_to_sqlite()
