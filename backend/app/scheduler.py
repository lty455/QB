# app/scheduler.py
import os
from urllib.parse import urlparse
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# === 【核心导入】引入你的 worker 中的任务队列 ===
from app.crawler.worker import crawl_queue
# === 【新增导入】引入你的大模型评分任务 ===
from app.tasks.scores_auto import run_daily_scoring
# === 【新增导入】引入刚才写的监控模块 ===
from app.monitor import init_db, lightweight_rss_sniff
# TXT 文件的路径 (请根据你的实际情况修改)
TXT_FILE_PATH = "./urls.txt"  # 假设在项目根目录


def get_websites_from_txt():
    """从 TXT 文件读取 URL 并构造成 worker 需要的字典格式"""
    websites = []

    if not os.path.exists(TXT_FILE_PATH):
        print(f"❌ 找不到 URL 文件: {TXT_FILE_PATH}")
        return websites

    with open(TXT_FILE_PATH, 'r', encoding='utf-8') as f:
        # 读取所有行，并去除空白字符
        urls = [line.strip() for line in f if line.strip()]

    for idx, url in enumerate(urls):
        # 提取域名，用于日志或生成简单的 ID
        try:
            domain = urlparse(url).netloc.replace('www.', '')
        except:
            domain = 'unknown'

        # 构造成核心爬虫需要的 website 字典格式
        # 注意：你的 worker.py 会调用 update_website_status(website['id'], ...)
        # 所以这里必须生成一个 id。
        website_info = {
            'id': f"txt_{idx}_{domain}",  # 生成一个虚拟ID，防止报错
            'url': url,
            'domain': domain
        }
        websites.append(website_info)

    return websites


def daily_crawl_job():
    """每天 23:50 触发的核心派单函数"""
    print(f"\n{'=' * 50}")
    print(f"⏰[定时任务启动] 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}\n")

    # 1. 锁定“今天”的日期 (格式: YYYY-MM-DD)，防止跨天
    locked_today_date = datetime.now().strftime('%Y-%m-%d')
    print(f"🔒 本次批量任务锁定的目标日期为: >= {locked_today_date}")

    # 2. 从 TXT 读取所有的网站
    websites = get_websites_from_txt()
    print(f"📂 从 TXT 文件中共读取到 {len(websites)} 个网站。")

    # 3. 构造任务参数，强制注入 target_date
    params = {
        'max_depth': 2,  # 你可以根据需要调整
        'max_pages': 50,
        'delay': 2.0,
        'timeout': 60,
        'target_date': locked_today_date  # 核心！传给 core.py 的日期
    }

    # 4. 遍历网站，推入 crawl_queue
    for website in websites:
        # 构造成 worker.py 期望的任务结构
        task = {
            'website': website,
            'params': params
        }

        # 将任务放入队列
        crawl_queue.put(task)

    print(f"✅[定时任务结束] {len(websites)} 个网站已成功推入队列，等待 Worker 消费。")


def start_scheduler():
    """启动后台调度器"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    #1. 设定每天 23:50 执行 daily_crawl_job
    scheduler.add_job(daily_crawl_job, 'cron', hour=23, minute=50)

    # 2. 【新增】主情报评分任务：每天中午 12:00 执行
    scheduler.add_job(run_daily_scoring, 'cron', hour=12, minute=0, id='main_scoring_job')

    scheduler.start()
    print("⏳ 后台定时调度器已启动 (等待每天 23:50 触发批量任务...)")