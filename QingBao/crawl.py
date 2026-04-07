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
from playwright.sync_api import sync_playwright
from app.config import CRAWL_DATA_DIR, DEFAULT_HEADERS

# === 【新增依赖】 ===
from htmldate import find_date
from dateutil.parser import parse as parse_date

# ---------- 动态域名列表（保持不变）----------
DYNAMIC_DOMAINS = [
    "whitehouse.gov", "afresearchlab.com", "discover.dtic.mil", "dsb.cto.mil",
    "inl.gov", "nasaspaceflight.com", "news.usni.org", "research-hub.nrel.gov",
    "acq.osd.mil", "army.mil", "businessdefense.gov", "cto.mil", "disa.mil",
    "erdcwerx.org", "mda.mil", "nasa.gov", "navair.navy.mil", "nga.mil",
    "niimbl.org", "sda.mil", "srnl.gov", "state.gov", "usni.org", "rand.org",
]


# ---------- 辅助函数 (extract_domain, is_valid_url, extract_all_links, is_likely_article_url 保持原样不变) ----------
def extract_domain(url):
    try:
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        return url.split('/')[0]
    except:
        return ''


def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except:
        return False


def extract_all_links(current_url, html_content, base_domain):
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


# === 【新增辅助函数】核心日期校验 ===
def check_date_filtering(html_content, url, limit_date_str):
    """如果提供了限制日期，检查文章是否满足要求"""
    if not limit_date_str:
        return False, None  # 没限制，直接放行

    try:
        found_date_str = find_date(html_content, url=url, outputformat='%Y-%m-%d')
        if found_date_str:
            limit_date = parse_date(limit_date_str).date()
            article_date = parse_date(found_date_str).date()
            if article_date < limit_date:
                return True, found_date_str  # 日期太老，跳过
            return False, found_date_str  # 日期符合，放行
        return False, None  # 找不到日期，默认放行
    except Exception as e:
        print(f"⚠️ 日期解析出错 {url}: {e}")
        return False, None


# === 【修改】保存逻辑：改为 Date/Domain 结构 ===
def save_article_to_file(article, website, article_number, target_date_str=None):
    """保存新闻文章到JSON文件"""
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)

    # 格式化日期文件夹 (YYMMDD)
    if target_date_str:
        try:
            date_folder = datetime.strptime(target_date_str, '%Y-%m-%d').strftime('%y%m%d')
        except ValueError:
            date_folder = datetime.now().strftime('%y%m%d')
    else:
        date_folder = datetime.now().strftime('%y%m%d')

    # 路径变为: data / 260318 / defense_gov
    site_dir = os.path.join(CRAWL_DATA_DIR, date_folder, safe_domain)
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


# === 【修改】保存逻辑：改为 Date/Domain/fallback 结构 ===
def save_page_as_fallback(url, html_content, website, page_number, target_date_str=None):
    """保存普通页面（非文章）为JSON文件"""
    domain = extract_domain(website['url'])
    safe_domain = re.sub(r'[^\w\-_]', '_', domain)

    if target_date_str:
        try:
            date_folder = datetime.strptime(target_date_str, '%Y-%m-%d').strftime('%y%m%d')
        except ValueError:
            date_folder = datetime.now().strftime('%y%m%d')
    else:
        date_folder = datetime.now().strftime('%y%m%d')

    # 路径变为: data / 260318 / defense_gov / fallback
    site_dir = os.path.join(CRAWL_DATA_DIR, date_folder, safe_domain, 'fallback')
    os.makedirs(site_dir, exist_ok=True)

    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(['script', 'style', 'meta', 'link']):
        script.decompose()

    text = soup.get_text(separator='\n', strip=True)
    title = soup.title.string.strip() if soup.title else '无标题'

    page_data = {
        'url': url,
        'title': title,
        'text': text[:50000],
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
    website_id = website['id']
    start_url = website['url']
    base_domain = extract_domain(start_url)

    max_depth = params.get('max_depth', 2)
    max_pages = params.get('max_pages', 30)
    delay = params.get('delay', 1.0)
    timeout = params.get('timeout', 60)

    # === 【获取定时任务注入的日期参数】 ===
    locked_limit_date = params.get('target_date')

    print(f"🔍 开始递归爬取: {start_url}")
    if locked_limit_date:
        print(f"🕒 本次任务指定抓取日期: >= {locked_limit_date}")

    try:
        # === 【修改】初始目录建立，统一按日期建立 ===
        safe_domain = re.sub(r'[^\w\-_]', '_', base_domain)
        if locked_limit_date:
            try:
                date_folder = datetime.strptime(locked_limit_date, '%Y-%m-%d').strftime('%y%m%d')
            except ValueError:
                date_folder = datetime.now().strftime('%y%m%d')
        else:
            date_folder = datetime.now().strftime('%y%m%d')

        site_dir = os.path.join(CRAWL_DATA_DIR, date_folder, safe_domain)
        os.makedirs(site_dir, exist_ok=True)

        active_tasks[website_id] = {
            'status': 'running',
            'total_pages': 0,
            'start_time': datetime.now().isoformat(),
            'params': params,
            'current_url': start_url
        }

        visited = set()
        to_visit = [(start_url, 0)]
        crawled_articles = []
        article_count = 0
        need_dynamic = any(domain in base_domain for domain in DYNAMIC_DOMAINS)

        while to_visit and article_count < max_pages:
            url, depth = to_visit.pop(0)

            if url in visited:
                continue
            visited.add(url)
            active_tasks[website_id]['current_url'] = url
            print(f"📄 爬取: {url} (深度: {depth}, 已找到: {article_count}/{max_pages})")

            html_content = None
            try:
                if need_dynamic:
                    try:
                        with sync_playwright() as p:
                            browser = p.chromium.launch(headless=True)
                            page = browser.new_page()
                            page.set_viewport_size({"width": 1920, "height": 1080})
                            page.set_extra_http_headers({
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'Accept-Language': 'en-US,en;q=0.9',
                            })
                            page.set_extra_http_headers(DEFAULT_HEADERS)
                            page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
                            page.wait_for_timeout(3000)
                            html_content = page.content()
                            browser.close()
                    except Exception as e:
                        print(f"❌ Playwright 渲染失败 {url}: {e}")
                        continue
                else:
                    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'text/html' not in content_type:
                        continue
                    html_content = response.text

            except Exception as e:
                print(f"❌ 请求失败 {url}: {e}")
                continue

            # ==========================================
            # 【新增】强力日期过滤拦截
            # ==========================================
            should_skip, extracted_date = check_date_filtering(html_content, url, locked_limit_date)

            if should_skip:
                print(f"⏭️ [日期过滤] 跳过旧文章 ({extracted_date} < {locked_limit_date}): {url}")
                continue
            # ==========================================

            try:
                article = None
                try:
                    article = NewsPlease.from_url(url, timeout=min(30, timeout))
                except Exception:
                    try:
                        article = NewsPlease.from_html(html_content, url=url)
                    except Exception as e2:
                        print(f"⚠️ NewsPlease提取失败: {e2}")
                        continue

                # ==========================================
                # 【新增】日期回填 (补全新闻对象缺失的日期)
                # ==========================================
                if article and extracted_date:
                    if not getattr(article, 'date_publish', None) or str(article.date_publish) == 'None':
                        article.date_publish = extracted_date
                # ==========================================

                is_article = False
                if (article and
                        hasattr(article, 'maintext') and
                        article.maintext and
                        len(article.maintext.strip()) > 200 and
                        hasattr(article, 'title') and
                        article.title and
                        len(article.title.strip()) > 3):
                    article_count += 1

                    # 【传入 locked_limit_date 以生成子目录】
                    save_article_to_file(article, website, article_count, locked_limit_date)

                    active_tasks[website_id]['total_pages'] = article_count
                    crawled_articles.append({
                        'title': article.title[:100],
                        'url': url,
                        'word_count': len(article.maintext)
                    })
                    print(f"✅ 找到文章 {article_count}/{max_pages}: {article.title[:60]}...")
                    is_article = True

                if not is_article:
                    page_count_fallback = article_count + 1
                    # 【传入 locked_limit_date 以生成子目录】
                    # save_page_as_fallback(url, html_content, website, page_count_fallback, locked_limit_date)
                    print(f"📄 保存普通页面: {url}")

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
            'articles': crawled_articles[:10]
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
        if website_id in active_tasks:
            del active_tasks[website_id]