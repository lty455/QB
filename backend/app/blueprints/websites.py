import os
import re
import json
from flask import Blueprint, jsonify, request

from app.models import load_all_websites, get_website_by_id
from app.crawler.worker import active_tasks
from app.config import CRAWL_DATA_DIR
from app.utils.helpers import extract_domain

websites_bp = Blueprint('websites', __name__, url_prefix='/api/websites')


@websites_bp.route('', methods=['GET'])
def get_websites():
    """获取网站列表，支持分页和统计"""
    try:
        websites = load_all_websites()

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 550, type=int)

        categories = {}
        status_count = {}

        for w in websites:
            cat = w['category']
            categories[cat] = categories.get(cat, 0) + 1
            status = w['status']
            status_count[status] = status_count.get(status, 0) + 1

        total = len(websites)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_websites = websites[start_idx:end_idx]

        return jsonify({
            'success': True,
            'data': {
                'websites': paginated_websites,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'total_pages': (total + page_size - 1) // page_size
                },
                'stats': {
                    'total': total,
                    'by_category': categories,
                    'by_status': status_count
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@websites_bp.route('/<int:website_id>/crawl-status', methods=['GET'])
def get_website_crawl_status(website_id):
    """获取指定网站的爬取状态"""
    # 优先检查活跃任务（正在运行）
    if website_id in active_tasks:
        task_info = active_tasks[website_id]
        return jsonify({
            'success': True,
            'is_running': True,
            'status': '抓取中',
            'progress': {
                'current_url': task_info.get('current_url', ''),
                'total_pages': task_info.get('total_pages', 0),
                'start_time': task_info.get('start_time', '')
            }
        })
    else:
        # 从数据库查询
        website = get_website_by_id(website_id)
        if not website:
            return jsonify({'success': False, 'error': '网站不存在'})

        return jsonify({
            'success': True,
            'is_running': False,
            'status': website['status'],
            'last_crawl': website.get('last_crawl'),
            'total_pages': website.get('total_pages', 0)
        })


@websites_bp.route('/<int:website_id>/crawled-articles', methods=['GET'])
def get_crawled_articles(website_id):
    """获取已爬取的文章列表（从文件读取）"""
    try:
        # 先获取网站信息
        website = get_website_by_id(website_id)
        if not website:
            return jsonify({'success': False, 'error': '网站不存在'})

        domain = extract_domain(website['url'])
        safe_domain = re.sub(r'[^\w\-_]', '_', domain)
        site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain)

        if not os.path.exists(site_dir):
            return jsonify({
                'success': True,
                'data': {
                    'articles': [],
                    'total': 0
                }
            })

        articles = []
        # 只读取网站主目录下的 JSON 文件（文章文件），忽略 fallback 子目录
        for filename in os.listdir(site_dir):
            if filename.endswith('.json') and filename.startswith('article_'):
                filepath = os.path.join(site_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                    articles.append({
                        'title': article_data.get('title', ''),
                        'url': article_data.get('url', ''),
                        'crawled_at': article_data.get('crawled_at', ''),
                        'word_count': len(article_data.get('text', ''))
                    })
                except:
                    continue

        # 按爬取时间倒序
        articles.sort(key=lambda x: x['crawled_at'], reverse=True)

        return jsonify({
            'success': True,
            'data': {
                'articles': articles[:50],  # 最多返回50篇
                'total': len(articles)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500