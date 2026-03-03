# app/crawler/worker.py
import threading
import queue
import asyncio
from app.crawler.core import recursive_crawl_website
from app.models import update_website_status

crawl_queue = queue.Queue()
active_tasks = {}      # 存储正在运行的任务信息
crawl_threads = []

def crawl_worker(worker_id):
    """工作线程函数"""
    # 为当前线程设置事件循环（解决 requests-html 的 asyncio 问题）
    try:
        # 尝试获取当前线程的事件循环
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # 如果没有，则创建一个新的事件循环并设置为当前线程的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    print(f"👷 爬虫工作线程 {worker_id} 启动")

    while True:
        try:
            task = crawl_queue.get(timeout=30)
            if task is None:
                break

            website = task['website']
            params = task.get('params', {})

            # 更新数据库状态为“抓取中”
            update_website_status(website['id'], '抓取中')

            # 执行核心爬取（此时线程已有事件循环）
            result = recursive_crawl_website(website, params, active_tasks)

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


def start_workers(num_workers=3):
    """启动指定数量的爬虫工作线程"""
    for i in range(num_workers):
        thread = threading.Thread(target=crawl_worker, args=(i + 1,), daemon=True)
        thread.start()
        crawl_threads.append(thread)
    print(f"✅ 已启动 {num_workers} 个爬虫工作线程")