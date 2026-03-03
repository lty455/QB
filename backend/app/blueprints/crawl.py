from flask import Blueprint, request, jsonify

from app.models import get_website_by_id, get_crawl_statistics
from app.crawler.worker import crawl_queue, active_tasks, crawl_threads

crawl_bp = Blueprint('crawl', __name__, url_prefix='/api')


@crawl_bp.route('/websites/<int:website_id>/recursive-crawl', methods=['POST'])
def recursive_crawl_single(website_id):
    """递归爬取单个网站"""
    data = request.json or {}
    params = data.get('params', {})

    website = get_website_by_id(website_id)
    if not website:
        return jsonify({'success': False, 'error': '网站不存在'})

    # 检查是否已经在爬取中
    if website_id in active_tasks:
        return jsonify({
            'success': False,
            'error': '该网站已经在爬取中'
        })

    task = {
        'website': website,
        'params': {
            'max_pages': params.get('max_pages', 30),
            'max_depth': params.get('max_depth', 2),
            'delay': params.get('delay', 1.0),
            'timeout': params.get('timeout', 60),
            'recursive': params.get('recursive', True)
        }
    }
    crawl_queue.put(task)

    return jsonify({
        'success': True,
        'message': f'已开始递归爬取 {website["url"]}',
        'website_id': website_id,
        'params': task['params']
    })


@crawl_bp.route('/websites/batch/recursive-crawl', methods=['POST'])
def batch_recursive_crawl():
    """批量递归爬取多个网站"""
    data = request.json or {}
    website_ids = data.get('website_ids', [])
    params = data.get('params', {})

    if not website_ids:
        return jsonify({'success': False, 'error': '未指定网站ID'})

    # 逐个获取网站信息并加入队列
    selected_websites = []
    for wid in website_ids:
        website = get_website_by_id(wid)
        if website:
            selected_websites.append(website)

    if not selected_websites:
        return jsonify({'success': False, 'error': '没有找到有效的网站'})

    for website in selected_websites:
        # 批量任务不检查 active_tasks（简化处理）
        task = {
            'website': website,
            'params': {
                'max_pages': params.get('max_pages', 30),
                'max_depth': params.get('max_depth', 2),
                'delay': params.get('delay', 1.0),
                'timeout': params.get('timeout', 60),
                'recursive': params.get('recursive', True)
            }
        }
        crawl_queue.put(task)

    return jsonify({
        'success': True,
        'message': f'已开始批量递归爬取 {len(selected_websites)} 个网站',
        'count': len(selected_websites)
    })


@crawl_bp.route('/crawl/params/presets', methods=['GET'])
def get_crawl_params_presets():
    """获取爬取参数预设"""
    return jsonify({
        'success': True,
        'presets': {
            'quick': {
                'name': '快速爬取',
                'max_pages': 10,
                'max_depth': 1,
                'delay': 0.5,
                'timeout': 30
            },
            'standard': {
                'name': '标准爬取',
                'max_pages': 30,
                'max_depth': 2,
                'delay': 1.0,
                'timeout': 60
            },
            'deep': {
                'name': '深度爬取',
                'max_pages': 50,
                'max_depth': 3,
                'delay': 2.0,
                'timeout': 120
            },
            'comprehensive': {
                'name': '全面爬取',
                'max_pages': 100,
                'max_depth': 3,
                'delay': 1.5,
                'timeout': 180
            }
        },
        'defaults': {
            'max_pages': 30,
            'max_depth': 2,
            'delay': 1.0,
            'timeout': 60,
            'recursive': True
        }
    })

@crawl_bp.route('/crawl/status', methods=['GET'])
def get_crawl_status():
    """获取爬虫整体状态（队列、活跃线程、统计等）"""
    queue_size = crawl_queue.qsize()
    active_threads = sum(1 for t in crawl_threads if t.is_alive())

    # 从数据库获取统计
    stats = get_crawl_statistics()
    total_websites = stats['total_websites']
    status_counts = stats['status_counts']
    total_pages = stats['total_pages']

    completed = status_counts.get('已完成', 0)
    pending = status_counts.get('待抓取', 0)
    processing = status_counts.get('抓取中', 0)
    failed = status_counts.get('失败', 0)

    completion_rate = round(completed / total_websites * 100, 2) if total_websites > 0 else 0

    # 当前正在运行的任务
    current_tasks = []
    for website_id, task_info in active_tasks.items():
        current_tasks.append({
            'website_id': website_id,
            'current_url': task_info.get('current_url', ''),
            'pages_crawled': task_info.get('total_pages', 0)
        })

    return jsonify({
        'success': True,
        'data': {
            'queue_size': queue_size,
            'active_workers': active_threads,
            'total_workers': len(crawl_threads),
            'active_tasks': len(active_tasks),
            'current_tasks': current_tasks,
            'statistics': {
                'total_websites': total_websites,
                'total_pages': total_pages,
                'completed': completed,
                'pending': pending,
                'processing': processing,
                'failed': failed,
                'completion_rate': completion_rate
            }
        }
    })