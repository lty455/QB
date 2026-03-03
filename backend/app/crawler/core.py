# app/crawler/core.py
import os
import json
import re
import time
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from newsplease import NewsPlease
# from requests_html import HTMLSession  # 新增导入
from playwright.sync_api import sync_playwright
from app.config import CRAWL_DATA_DIR, DEFAULT_HEADERS


# ---------- 动态域名列表（手动维护，后续可在此添加）----------
# 当爬取这些域名时，将使用 requests-html 渲染 JavaScript
DYNAMIC_DOMAINS = [
    "whitehouse.gov",
    # "acqnotes.com",
    # 可继续添加其他动态网站的主域名，如 "example.com"
    "afresearchlab.com", "discover.dtic.mil", "dsb.cto.mil", "inl.gov", "nasaspaceflight.com",
    "news.usni.org", "research-hub.nrel.gov", "acq.osd.mil", "army.mil", "businessdefense.gov",
    "cto.mil", "disa.mil", "erdcwerx.org", "mda.mil", "nasa.gov", "navair.navy.mil",
    "nga.mil", "niimbl.org", "sda.mil", "srnl.gov", "state.gov", "usni.org", "rand.org",
]


# ---------- 辅助函数 ----------
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
    """提取当前页面的所有链接，限制在同一主域名下"""
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

        parsed = urlparse(absolute_url)
        if base_netloc in parsed.netloc or parsed.netloc.endswith('.' + base_netloc):
            links.append(absolute_url)

    return list(set(links))


def is_likely_article_url(url):
    """简单判断URL是否可能是文章页面（排除非文章路径）"""
    url_lower = url.lower()
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


def save_article_to_file(article, website, article_number):
    """保存新闻文章到JSON文件"""
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)
    site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain)
    os.makedirs(site_dir, exist_ok=True)

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

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()[:8]
    filename = f"article_{article_number:03d}_{timestamp}_{url_hash}.json"
    filepath = os.path.join(site_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)

    return filepath


def save_page_as_fallback(url, html_content, website, page_number):
    """保存普通页面（非文章）为JSON文件"""
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)
    site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain, 'fallback')
    os.makedirs(site_dir, exist_ok=True)

    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(['script', 'style', 'meta', 'link']):
        script.decompose()

    text = soup.get_text(separator='\n', strip=True)
    title = soup.title.string.strip() if soup.title else '无标题'

    page_data = {
        'url': url,
        'title': title,
        'text': text[:50000],  # 限制长度
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


# ---------- 核心爬取函数 ----------
def recursive_crawl_website(website, params, active_tasks):
    """
    基于BFS的递归爬取，返回爬取结果摘要
    :param website: 网站信息字典（包含 id, url, domain 等）
    :param params: 爬取参数字典（max_depth, max_pages, delay, timeout）
    :param active_tasks: 全局活跃任务字典（用于更新当前URL和进度，便于前端实时监控）
    :return: 结果字典（success, website_id, pages_crawled, message, articles）
    """
    website_id = website['id']
    start_url = website['url']
    base_domain = extract_domain(start_url)

    max_depth = params.get('max_depth', 2)
    max_pages = params.get('max_pages', 30)
    delay = params.get('delay', 1.0)
    timeout = params.get('timeout', 60)

    print(f"🔍 开始递归爬取: {start_url}")
    print(f"📊 爬取参数: 深度={max_depth}, 最大文章数={max_pages}, 延迟={delay}s")

    try:
        # 创建网站专属目录（确保存在）
        safe_domain = re.sub(r'[^\w\-_]', '_', base_domain)
        site_dir = os.path.join(CRAWL_DATA_DIR, safe_domain)
        os.makedirs(site_dir, exist_ok=True)

        # 在 active_tasks 中注册任务
        active_tasks[website_id] = {
            'status': 'running',
            'total_pages': 0,
            'start_time': datetime.now().isoformat(),
            'params': params,
            'current_url': start_url
        }

        visited = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        crawled_articles = []
        article_count = 0

        # 判断当前域名是否需要动态渲染
        need_dynamic = any(domain in base_domain for domain in DYNAMIC_DOMAINS)

        while to_visit and article_count < max_pages:
            url, depth = to_visit.pop(0)

            if url in visited:
                continue
            visited.add(url)

            # 更新当前正在爬取的URL（用于前端实时显示）
            active_tasks[website_id]['current_url'] = url

            print(f"📄 爬取: {url} (深度: {depth}, 已找到: {article_count}/{max_pages})")

            # ---------- 智能请求部分 ----------
            html_content = None
            try:
                if need_dynamic:
                    try:
                        with sync_playwright() as p:
                            # 启动浏览器（headless 无头模式）
                            browser = p.chromium.launch(headless=True)
                            page = browser.new_page()
                            page.set_viewport_size({"width": 1920, "height": 1080})
                            page.set_extra_http_headers({
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'Accept-Language': 'en-US,en;q=0.9',
                            })
                            # 设置请求头（可选）
                            page.set_extra_http_headers(DEFAULT_HEADERS)
                            # 访问页面，等待直到网络空闲（或指定时间）
                            page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
                            # 等待特定元素出现（根据网站结构调整，这里等待3秒后获取内容）
                            page.wait_for_timeout(3000)  # 等待3秒
                            html_content = page.content()
                            browser.close()
                    except Exception as e:
                        print(f"❌ Playwright 渲染失败 {url}: {e}")
                        continue
                else:
                    # 使用普通 requests
                    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'text/html' not in content_type:
                        print(f"⚠️ 跳过非HTML内容: {content_type}")
                        continue
                    html_content = response.text

            except Exception as e:
                print(f"❌ 请求失败 {url}: {e}")
                continue

            # ---------- 后续处理（保持不变）----------
            try:
                # 尝试用 NewsPlease 提取文章
                article = None
                try:
                    article = NewsPlease.from_url(url, timeout=min(30, timeout))
                except Exception:
                    try:
                        article = NewsPlease.from_html(html_content, url=url)
                    except Exception as e2:
                        print(f"⚠️ NewsPlease提取失败: {e2}")
                        continue

                # 判断是否为合格文章
                is_article = False
                if (article and
                        hasattr(article, 'maintext') and
                        article.maintext and
                        len(article.maintext.strip()) > 200 and
                        hasattr(article, 'title') and
                        article.title and
                        len(article.title.strip()) > 3):
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

                # 如果不是文章，保存为普通页面
                if not is_article:
                    # 使用 article_count + 1 作为页码（仅用于文件命名，不占用文章计数）
                    page_count_fallback = article_count + 1
                    save_page_as_fallback(url, html_content, website, page_count_fallback)
                    print(f"📄 保存普通页面: {url}")

                # 如果未达到最大深度，提取链接继续爬取
                if depth < max_depth:
                    try:
                        links = extract_all_links(url, html_content, base_domain)
                        filtered_links = [link for link in links if is_likely_article_url(link)]

                        for link in filtered_links:
                            if link not in visited and link not in [u for u, _ in to_visit]:
                                to_visit.append((link, depth + 1))

                        print(f"🔗 提取到 {len(filtered_links)}/{len(links)} 个链接，队列长度: {len(to_visit)}")
                    except Exception as e:
                        print(f"⚠️ 提取链接失败: {e}")

                time.sleep(delay)

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
        # 任务结束，从 active_tasks 中移除
        if website_id in active_tasks:
            del active_tasks[website_id]