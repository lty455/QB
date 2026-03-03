import pymysql
from app.config import DB_CONFIG
from datetime import datetime

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def load_all_websites():
    # 返回所有网站列表（字典格式）
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM websites ORDER BY id")
    rows = cursor.fetchall()
    # 转换为与原 JSON 结构一致
    websites = []
    for row in rows:
        websites.append({
            'id': row['id'],
            'url': row['url'],
            'domain': row['domain'],
            'category': row['category'],
            'status': row['status'],
            'last_crawl': row['last_crawl'].isoformat() if row['last_crawl'] else None,
            'total_pages': row['total_pages'] or 0,
            'error': row['error'],
            'progress': float(row['progress'] or 0),
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
        })
    cursor.close()
    conn.close()
    return websites

def update_website_status(website_id, status, error=None, pages_crawled=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status == '已完成':
        sql = "UPDATE websites SET status=%s, last_crawl=%s, total_pages=%s, error=%s WHERE id=%s"
        params = (status, datetime.now(), pages_crawled, error, website_id)
    else:
        sql = "UPDATE websites SET status=%s, error=%s WHERE id=%s"
        params = (status, error, website_id)
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

def get_website_by_id(website_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, domain, category, status FROM websites WHERE id=%s", (website_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_crawl_statistics():
    """返回爬虫整体统计数据：总网站数、各状态计数、总页面数"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 总数
        cursor.execute("SELECT COUNT(*) as total FROM websites")
        total_websites = cursor.fetchone()['total']

        # 按状态分组
        cursor.execute("SELECT status, COUNT(*) as cnt FROM websites GROUP BY status")
        rows = cursor.fetchall()
        status_counts = {row['status']: row['cnt'] for row in rows}

        # 总页面数
        cursor.execute("SELECT SUM(total_pages) as total_pages FROM websites")
        total_pages = cursor.fetchone()['total_pages'] or 0

        return {
            'total_websites': total_websites,
            'status_counts': status_counts,
            'total_pages': total_pages
        }
    finally:
        cursor.close()
        conn.close()