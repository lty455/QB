
import os
import json
import re
import time
import threading
import queue
import requests
import hashlib
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from newsplease import NewsPlease
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

# 配置文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WEBSITES_FILE = os.path.join(DATA_DIR, 'websites.txt')
WEBSITES_JSON = os.path.join(DATA_DIR, 'websites.json')
CRAWL_DATA_DIR = os.path.join(DATA_DIR, 'websites')
file_lock = threading.Lock()  # 添加文件锁
# 爬虫任务队列
crawl_queue = queue.Queue()
crawl_threads = []

# 当前运行的任务
active_tasks = {}

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


def extract_domain(url):
    """从URL提取主域名"""
    try:
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        return url.split('/')[0]
    except:
        return ''


def is_valid_url(url):
    """检查URL是否有效"""
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except:
        return False


def extract_all_links(current_url, html_content, base_domain):
    """提取当前页面的所有链接，不局限于同域名（可选）"""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    base_netloc = urlparse(base_domain).netloc if base_domain.startswith('http') else base_domain

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue

        absolute_url = urljoin(current_url, href)
        if not is_valid_url(absolute_url):
            continue

        # 可选：放宽限制，允许所有http链接（慎用，可能爬出站）
        # 目前仍建议限制在同一主域名下，但处理www变体
        parsed = urlparse(absolute_url)
        if base_netloc in parsed.netloc or parsed.netloc.endswith('.' + base_netloc):
            links.append(absolute_url)

    return list(set(links))

def is_likely_article_url(url):
    """简单判断URL是否可能是文章页面"""
    url_lower = url.lower()

    # 排除明显不是文章的页面
    exclude_patterns = [
        r'login', r'logout', r'signin', r'signup', r'register',
        r'user/', r'profile/', r'account/', r'my/', r'personal/',
        r'setting', r'admin', r'dashboard', r'cart', r'checkout',
        r'password', r'auth', r'oauth',
        r'collection', r'history', r'download', r'purchase',
        r'favorite', r'follow', r'statement', r'about', r'recruit',
        r'javascript:', r'mailto:', r'tel:', r'#commentform'
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, url_lower):
            return False

    return True


def load_websites_from_json():
    """从websites.json加载网站数据（线程安全）"""
    with file_lock:
        if not os.path.exists(WEBSITES_JSON):
            return []
        try:
            with open(WEBSITES_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('websites', [])
        except:
            return []

def save_websites_to_json(websites):
    """保存网站列表为JSON格式（线程安全）"""
    with file_lock:
        data = {
            'websites': websites,
            'total': len(websites),
            'last_updated': datetime.now().isoformat()
        }
        with open(WEBSITES_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def update_website_status(website_id, status, error=None, pages_crawled=0):
    """更新网站状态"""
    websites = load_websites_from_json()

    for website in websites:
        if website['id'] == website_id:
            website['status'] = status
            website['last_crawl'] = datetime.now().isoformat() if status == '已完成' else None
            website['error'] = error
            if status == '已完成':
                website['total_pages'] = pages_crawled
            break

    save_websites_to_json(websites)


def save_article_to_file(article, website, article_number):
    """保存文章到文件"""
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)
    site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain)
    os.makedirs(site_dir, exist_ok=True)

    # 准备文章数据
    article_data = {
        'url': article.url if hasattr(article, 'url') else '',
        'title': article.title if hasattr(article, 'title') else '',
        'description': article.description if hasattr(article, 'description') else '',
        'text': article.maintext if hasattr(article, 'maintext') else '',
        'authors': article.authors if hasattr(article, 'authors') else [],
        'date_publish': str(article.date_publish) if hasattr(article, 'date_publish') else None,
        'language': article.language if hasattr(article, 'language') else '',
        'source_domain': article.source_domain if hasattr(article, 'source_domain') else '',
        'crawled_at': datetime.now().isoformat(),
        'parent_url': website['url'],
        'article_number': article_number,
        'website_id': website['id']
    }

    # 生成唯一文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()[:8]
    filename = f"article_{article_number:03d}_{timestamp}_{url_hash}.json"
    filepath = os.path.join(site_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)

    return filepath


def recursive_crawl_website(website, params):
    """基于BFS的递归爬取（简洁高效版）"""
    website_id = website['id']
    start_url = website['url']
    base_domain = extract_domain(start_url)

    # 爬取参数
    max_depth = params.get('max_depth', 2)
    max_pages = params.get('max_pages', 30)
    delay = params.get('delay', 1.0)
    timeout = params.get('timeout', 60)

    print(f"🔍 开始递归爬取: {start_url}")
    print(f"📊 爬取参数: 深度={max_depth}, 最大文章数={max_pages}, 延迟={delay}s")

    try:
        # 创建保存目录
        safe_domain = re.sub(r'[^\w\-_]', '_', base_domain)
        site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain)
        os.makedirs(site_dir, exist_ok=True)

        # 更新任务状态
        active_tasks[website_id] = {
            'status': 'running',
            'total_pages': 0,
            'start_time': datetime.now().isoformat(),
            'params': params,
            'current_url': start_url
        }

        # BFS数据结构
        visited = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        crawled_articles = []
        article_count = 0

        while to_visit and article_count < max_pages:
            url, depth = to_visit.pop(0)

            # 跳过已访问
            if url in visited:
                continue

            visited.add(url)

            # 更新当前爬取的URL（用于前端显示）
            active_tasks[website_id]['current_url'] = url

            print(f"📄 爬取: {url} (深度: {depth}, 已找到: {article_count}/{max_pages})")

            try:
                # 1. 下载页面
                response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
                response.raise_for_status()

                # 检查内容类型
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    print(f"⚠️ 跳过非HTML内容: {content_type}")
                    continue

                # 2. 尝试用NewsPlease提取文章
                article = None
                try:
                    article = NewsPlease.from_url(url, timeout=min(30, timeout))
                except Exception as e:
                    # 如果from_url失败，尝试from_html
                    try:
                        article = NewsPlease.from_html(response.text, url=url)
                    except Exception as e2:
                        print(f"⚠️ NewsPlease提取失败: {e2}")
                        continue

                # 3. 如果是有效的文章，保存
                # 3. 处理页面内容：优先保存为文章，否则保存为普通页面
                is_article = False
                if (article and
                        hasattr(article, 'maintext') and
                        article.maintext and
                        len(article.maintext.strip()) > 200 and
                        hasattr(article, 'title') and
                        article.title and
                        len(article.title.strip()) > 3):
                    # 是文章，保存结构化数据
                    article_count += 1
                    save_article_to_file(article, website, article_count)
                    active_tasks[website_id]['total_pages'] = article_count
                    crawled_articles.append({
                        'title': article.title[:100],
                        'url': url,
                        'word_count': len(article.maintext)
                    })
                    print(f"✅ 找到文章 {article_count}/{max_pages}: {article.title[:60]}...")
                    is_article = True

                # 如果不是文章，或者你想保存所有页面（包括文章也额外保存HTML），可以取消下面的注释
                # 但注意：如果上面已经保存了文章，这里再保存HTML可能会重复，你可以根据需要决定
                if not is_article:
                    # 后备：保存普通页面（提取纯文本）
                    page_count_fallback = article_count + 1  # 如果文章计数未增加，单独计数
                    save_page_as_fallback(url, response.text, website, page_count_fallback)
                    print(f"📄 保存普通页面: {url}")
                    # 如果也想计数，可以增加一个普通页面计数器

                # 4. 如果还有深度，提取链接继续爬取
                if depth < max_depth:
                    try:
                        links = extract_all_links(url, response.text, base_domain)

                        # 过滤掉不太可能是文章的URL（可选）
                        filtered_links = [link for link in links if is_likely_article_url(link)]

                        # 添加到待访问队列
                        for link in filtered_links:
                            if link not in visited and link not in [u for u, _ in to_visit]:
                                to_visit.append((link, depth + 1))

                        print(f"🔗 提取到 {len(filtered_links)}/{len(links)} 个链接，队列长度: {len(to_visit)}")
                    except Exception as e:
                        print(f"⚠️ 提取链接失败: {e}")

                # 5. 延迟，避免被封
                time.sleep(delay)

            except requests.RequestException as e:
                print(f"❌ 请求失败 {url}: {e}")
                continue
            except Exception as e:
                print(f"❌ 处理页面失败 {url}: {e}")
                continue

        print(f"✅ 递归爬取完成: {start_url}, 爬取了 {article_count} 个文章页面")
        return {
            'success': article_count > 0,
            'website_id': website_id,
            'pages_crawled': article_count,
            'message': f'爬取完成，找到 {article_count} 篇文章',
            'articles': crawled_articles[:10]  # 只返回前10篇作为预览
        }

    except Exception as e:
        error_msg = f"递归爬取失败: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'website_id': website_id,
            'message': error_msg,
            'pages_crawled': 0
        }
    finally:
        # 清理任务状态
        if website_id in active_tasks:
            del active_tasks[website_id]


def save_page_as_fallback(url, html_content, website, page_number):
    """保存普通页面（非文章）到文件"""
    from bs4 import BeautifulSoup
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)
    site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain, 'fallback')  # 单独放在fallback子目录，便于区分
    os.makedirs(site_dir, exist_ok=True)

    soup = BeautifulSoup(html_content, 'html.parser')

    # 移除脚本、样式等标签
    for script in soup(['script', 'style', 'meta', 'link']):
        script.decompose()

    # 提取纯文本
    text = soup.get_text(separator='\n', strip=True)
    # 提取标题（如果存在）
    title = soup.title.string.strip() if soup.title else '无标题'

    page_data = {
        'url': url,
        'title': title,
        'text': text[:50000],  # 限制长度，避免过大
        'crawled_at': datetime.now().isoformat(),
        'parent_url': website['url'],
        'page_number': page_number,
        'website_id': website['id'],
        'type': 'fallback_page'
    }

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"page_{page_number:03d}_{timestamp}_{url_hash}.json"
    filepath = os.path.join(site_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, ensure_ascii=False, indent=2)

    return filepath

def crawl_worker(worker_id):
    """爬虫工作线程"""
    print(f"👷 爬虫工作线程 {worker_id} 启动")

    while True:
        try:
            task = crawl_queue.get(timeout=30)
            if task is None:
                break

            website = task['website']
            params = task.get('params', {})

            # 更新状态为抓取中
            update_website_status(website['id'], '抓取中')

            # 执行递归爬取
            result = recursive_crawl_website(website, params)

            # 更新状态为完成或失败
            if result['success']:
                update_website_status(
                    website['id'],
                    '已完成',
                    pages_crawled=result.get('pages_crawled', 1)
                )
            else:
                update_website_status(
                    website['id'],
                    '失败',
                    error=result['message']
                )

            crawl_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"❌ 工作线程 {worker_id} 错误: {str(e)}")


@app.route('/api/websites', methods=['GET'])
def get_websites():
    """获取网站列表"""
    try:
        websites = load_websites_from_json()

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 100, type=int)

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


@app.route('/api/websites/<int:website_id>/recursive-crawl', methods=['POST'])
def recursive_crawl_single_website(website_id):
    """递归爬取单个网站"""
    data = request.json
    params = data.get('params', {})

    websites = load_websites_from_json()
    website = None

    for w in websites:
        if w['id'] == website_id:
            website = w
            break

    if not website:
        return jsonify({'success': False, 'error': '网站不存在'})

    # 检查是否已经在爬取中
    if website_id in active_tasks:
        return jsonify({
            'success': False,
            'error': '该网站已经在爬取中'
        })

    # 将任务放入队列
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


@app.route('/api/websites/batch/recursive-crawl', methods=['POST'])
def batch_recursive_crawl_websites():
    """批量递归爬取网站"""
    data = request.json
    website_ids = data.get('website_ids', [])
    params = data.get('params', {})

    websites = load_websites_from_json()
    selected_websites = []

    for w in websites:
        if w['id'] in website_ids:
            selected_websites.append(w)

    if not selected_websites:
        return jsonify({'success': False, 'error': '没有找到符合条件的网站'})

    # 将任务放入队列
    for website in selected_websites:
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


@app.route('/api/websites/<int:website_id>/crawl-status', methods=['GET'])
def get_website_crawl_status(website_id):
    """获取网站爬取状态"""
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
        # 检查网站状态
        websites = load_websites_from_json()
        for w in websites:
            if w['id'] == website_id:
                return jsonify({
                    'success': True,
                    'is_running': False,
                    'status': w['status'],
                    'last_crawl': w.get('last_crawl'),
                    'total_pages': w.get('total_pages', 0)
                })

        return jsonify({
            'success': False,
            'error': '网站不存在'
        })


@app.route('/api/crawl/status', methods=['GET'])
def get_crawl_status():
    """获取爬虫状态"""
    queue_size = crawl_queue.qsize()
    active_threads = sum(1 for t in crawl_threads if t.is_alive())

    # 获取统计信息
    websites = load_websites_from_json()
    total_websites = len(websites)
    completed = sum(1 for w in websites if w['status'] == '已完成')
    pending = sum(1 for w in websites if w['status'] == '待抓取')
    processing = sum(1 for w in websites if w['status'] == '抓取中')
    failed = sum(1 for w in websites if w['status'] == '失败')

    # 统计总页面数
    total_pages = sum(w.get('total_pages', 0) for w in websites)

    # 获取当前活跃任务
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
                'completion_rate': round(completed / total_websites * 100, 2) if total_websites > 0 else 0
            }
        }
    })


# @app.route('/api/crawl/params/presets', methods=['GET'])
# def get_crawl_params_presets():
#     """获取爬取参数预设"""
#     return jsonify({
#         'success': True,
#         'presets': {
#             'quick': {
#                 'name': '快速爬取',
#                 'max_pages': 10,
#                 'max_depth': 1,
#                 'delay': 0.5,
#                 'timeout': 30
#             },
#             'standard': {
#                 'name': '标准爬取',
#                 'max_pages': 30,
#                 'max_depth': 2,
#                 'delay': 1.0,
#                 'timeout': 60
#             },
#             'deep': {
#                 'name': '深度爬取',
#                 'max_pages': 50,
#                 'max_depth': 3,
#                 'delay': 2.0,
#                 'timeout': 120
#             },
#             'comprehensive': {
#                 'name': '全面爬取',
#                 'max_pages': 100,
#                 'max_depth': 3,
#                 'delay': 1.5,
#                 'timeout': 180
#             }
#         },
#         'defaults': {
#             'max_pages': 30,
#             'max_depth': 2,
#             'delay': 1.0,
#             'timeout': 60,
#             'recursive': True
#         }
#     })


@app.route('/api/websites/<int:website_id>/crawled-articles', methods=['GET'])
def get_crawled_articles(website_id):
    """获取已爬取的文章列表"""
    try:
        websites = load_websites_from_json()
        website = None

        for w in websites:
            if w['id'] == website_id:
                website = w
                break

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

        # 读取所有文章文件
        articles = []
        for filename in os.listdir(site_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(site_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)

                        # 只返回关键信息
                        articles.append({
                            'title': article_data.get('title', ''),
                            'url': article_data.get('url', ''),
                            'crawled_at': article_data.get('crawled_at', ''),
                            'word_count': len(article_data.get('text', ''))
                        })
                except:
                    continue

        # 按爬取时间排序
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


def init_crawl_workers(num_workers=3):
    """初始化爬虫工作线程"""
    for i in range(num_workers):
        thread = threading.Thread(target=crawl_worker, args=(i + 1,))
        thread.daemon = True
        thread.start()
        crawl_threads.append(thread)
    print(f"✅ 已启动 {num_workers} 个爬虫工作线程")


if __name__ == '__main__':
    # 创建数据目录
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CRAWL_DATA_DIR, exist_ok=True)

    print("📦 检查依赖库...")
    try:
        from newsplease import NewsPlease

        print("✅ news-please 已安装")
    except ImportError as e:
        print(f"❌ news-please 未安装: {e}")
        print("   请运行: pip install news-please==1.5.34")
        exit(1)

    # 检查其他依赖
    try:
        import requests
        from bs4 import BeautifulSoup

        print("✅ requests 和 BeautifulSoup 已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("   请运行: pip install requests beautifulsoup4")
        exit(1)

    # 如果网站文件不存在，创建一个示例
    if not os.path.exists(WEBSITES_FILE):
        with open(WEBSITES_FILE, 'w', encoding='utf-8') as f:
            f.write("# 网站列表\n")
            f.write("https://news.sina.com.cn | 新闻\n")
            f.write("https://www.163.com | 新闻\n")
            f.write("https://www.csdn.net | 技术\n")
            f.write("https://www.cnblogs.com | 技术\n")
            f.write("https://www.jianshu.com | 文学\n")
            f.write("https://www.zhihu.com | 问答\n")

    # 初始化数据
    if not os.path.exists(WEBSITES_JSON):
        websites = []
        with open(WEBSITES_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('|')
                if len(parts) >= 1:
                    url = parts[0].strip()
                    category = parts[1].strip() if len(parts) > 1 else '新闻'

                    websites.append({
                        'id': i + 1,
                        'url': url,
                        'domain': extract_domain(url),
                        'category': category,
                        'status': '待抓取',
                        'last_crawl': None,
                        'total_pages': 0,
                        'error': None,
                        'progress': 0,
                        'created_at': datetime.now().isoformat()
                    })

        save_websites_to_json(websites)
        print(f"✅ 已初始化 {len(websites)} 个网站")

    # 启动爬虫工作线程
    init_crawl_workers(3)

    print(f"\n🚀 递归爬虫服务启动完成")
    print(f"📊 数据源: {WEBSITES_JSON}")
    print(f"📁 爬虫数据: {CRAWL_DATA_DIR}")
    print(f"🌐 访问地址: http://localhost:5000")
    print(f"\n🔗 主要API端点:")
    print(f"  - GET  /api/websites                    # 获取网站列表")
    print(f"  - POST /api/websites/<id>/recursive-crawl    # 递归爬取单个网站")
    print(f"  - GET  /api/crawl/params/presets       # 获取爬取参数预设")
    print(f"  - GET  /api/websites/<id>/crawl-status # 查看爬取状态")
    print(f"  - GET  /api/websites/<id>/crawled-articles # 查看已爬取文章")
    print(f"\n⚙️  默认爬取参数:")
    print(f"  - 最大文章数: 30")
    print(f"  - 最大深度: 2")
    print(f"  - 延迟: 1.0秒")
    print(f"  - 超时: 60秒")
    print(f"  - 递归: 是")

    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
