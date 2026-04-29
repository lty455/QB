from app.database import get_connection
from datetime import datetime


def get_db_connection():
    """获取数据库连接（适配器）"""
    return get_connection()

def load_all_websites():
    # 返回所有网站列表（字典格式）
    adapter = get_db_connection()
    rows = adapter.fetch_all("SELECT * FROM websites ORDER BY id")
    
    # 转换为与原 JSON 结构一致
    websites = []
    for row in rows:
        # 处理日期时间字段
        last_crawl = row.get('last_crawl')
        created_at = row.get('created_at')
        
        # SQLite 返回字符串，MySQL 返回 datetime 对象
        if last_crawl and hasattr(last_crawl, 'isoformat'):
            last_crawl = last_crawl.isoformat()
        if created_at and hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        
        websites.append({
            'id': row['id'],
            'url': row['url'],
            'domain': row['domain'],
            'category': row['category'],
            'status': row['status'],
            'last_crawl': last_crawl,
            'total_pages': row['total_pages'] or 0,
            'error': row['error'],
            'progress': float(row['progress'] or 0),
            'created_at': created_at,
        })
    
    return websites

def update_website_status(website_id, status, error=None, pages_crawled=0):
    adapter = get_db_connection()
    try:
        if status == '已完成':
            sql = "UPDATE websites SET status=?, last_crawl=?, total_pages=?, error=? WHERE id=?"
            params = (status, datetime.now(), pages_crawled, error, website_id)
        else:
            sql = "UPDATE websites SET status=?, error=? WHERE id=?"
            params = (status, error, website_id)
        
        adapter.execute(sql, params)
        adapter.commit()
    except Exception as e:
        adapter.rollback()
        print(f"更新网站状态失败: {e}")
        raise

def get_website_by_id(website_id):
    adapter = get_db_connection()
    row = adapter.fetch_one("SELECT id, url, domain, category, status FROM websites WHERE id=?", (website_id,))
    return row

def get_crawl_statistics():
    """返回爬虫整体统计数据：总网站数、各状态计数、总页面数"""
    adapter = get_db_connection()
    try:
        # 总数
        result = adapter.fetch_one("SELECT COUNT(*) as total FROM websites")
        total_websites = result['total'] if result else 0

        # 按状态分组
        rows = adapter.fetch_all("SELECT status, COUNT(*) as cnt FROM websites GROUP BY status")
        status_counts = {row['status']: row['cnt'] for row in rows}

        # 总页面数
        result = adapter.fetch_one("SELECT SUM(total_pages) as total_pages FROM websites")
        total_pages = result['total_pages'] if result and result['total_pages'] else 0

        return {
            'total_websites': total_websites,
            'status_counts': status_counts,
            'total_pages': total_pages
        }
    except Exception as e:
        print(f"获取爬虫统计信息失败: {e}")
        return {
            'total_websites': 0,
            'status_counts': {},
            'total_pages': 0
        }