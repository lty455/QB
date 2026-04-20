# app/monitor.py
import os
import sqlite3
import time
import feedparser
from datetime import datetime, timedelta, timezone
import statistics

# === 【优化路径】确保文件始终建在项目的根目录 ===
# 保持 BASE_DIR 指向 backend 目录（原写法不变）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DB_PATH 正确，无需修改
DB_PATH = os.path.join(BASE_DIR, 'traffic_monitor.db')

# RSS_FILE_PATH 修正：从 backend 再进入 app 目录
RSS_FILE_PATH = os.path.join(BASE_DIR, 'app', 'valid_rss.txt')
# ===================================================

# ===================================================

def init_db():
    """初始化用于记录流量的轻量级 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 记录每次扫描的时间和过去15分钟全网新增总数
    c.execute('''CREATE TABLE IF NOT EXISTS rss_traffic
                 (
                     timestamp
                     DATETIME,
                     new_count
                     INTEGER
                 )''')
    conn.commit()
    conn.close()


def get_rss_feeds():
    """每次执行时，实时从 txt 文件中读取最新的 RSS 列表"""
    if not os.path.exists(RSS_FILE_PATH):
        print(f"⚠️ 警告: 找不到 RSS 列表文件 '{RSS_FILE_PATH}'")
        return []

    with open(RSS_FILE_PATH, 'r', encoding='utf-8') as f:
        # 读取并过滤空行
        feeds = [line.strip() for line in f if line.strip()]

    return feeds


def fetch_recent_rss_count():
    rss_urls = get_rss_feeds()
    if not rss_urls:
        return 0, 0

    new_articles_count = 0

    # 1. 获取现在的精确 UTC 时间
    now_utc = datetime.now(timezone.utc)
    # 2. 过去 15 分钟的底线
    time_threshold = now_utc - timedelta(minutes=15)
    # 3. 【新增】未来时间的上限（允许 5 分钟的误差，防止某些网站服务器时间稍微超前）
    future_threshold = now_utc + timedelta(minutes=5)

    for rss_url in rss_urls:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)

                    # 【核心修改】：发布时间必须大于底线，且小于上限！
                    if time_threshold <= pub_time <= future_threshold:
                        new_articles_count += 1

                        # (可选) 如果你想抓出到底是哪两篇文章在捣鬼，可以加上这行打印：
                        # print(f"发现新文章: {entry.title} | 时间: {pub_time}")

        except Exception:
            continue

    return new_articles_count, len(rss_urls)


def lightweight_rss_sniff():
    """每 15 分钟执行一次的主监控函数"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动轻量级 RSS 流量雷达扫描...")

    # 1. 接收返回的两个数字
    current_count, total_sources = fetch_recent_rss_count()

    # 【补上漏掉的这行日志】
    if total_sources > 0:
        print(f"📡 正在监控 {total_sources} 个数据源...")
    print(f"📊 本次扫描：全网过去 30 分钟新增 {current_count} 篇文章")

    # 2. 存入数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO rss_traffic VALUES (?, ?)",
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), current_count))
    conn.commit()

    # 3. 提取历史数据，计算基线 (过去 24 小时)
    c.execute('''SELECT new_count
                 FROM rss_traffic
                 WHERE timestamp >= datetime('now', '-1 day')''')
    historical_data = [row[0] for row in c.fetchall()]
    conn.close()

    # 4. 异常突增检测算法 (Z-Score)
    # 至少积累了 4 个数据点 (1小时) 才开始报警计算，防止刚启动时误报
    if len(historical_data) >= 4:
        mean_val = statistics.mean(historical_data)
        try:
            stdev_val = statistics.stdev(historical_data)
        except statistics.StatisticsError:
            stdev_val = 0  # 数据全部一样时标准差为 0

        # 设定触发阈值：均值 + 3倍标准差 (且新增数量至少大于 5 篇，过滤绝对值极小的微小波动)
        threshold = mean_val + (3 * stdev_val)

        if current_count > threshold and current_count > 5:
            trigger_alert(current_count, mean_val, threshold)


def trigger_alert(current_count, mean_val, threshold):
    """触发告警动作"""
    msg = f"\n🚨🚨🚨 **重大情报预警** 🚨🚨🚨\n" \
          f"检测到全网资讯发布量异常激增！\n" \
          f"当前 15 分钟新增：{current_count} 篇\n" \
          f"平时正常均值约：{int(mean_val)} 篇 (触发阈值:{int(threshold)})\n" \
          f"可能有突发重大事件，请立即核查！\n" \
          f"{'=' * 40}"
    print(msg)
    # TODO: 这里可以加上 requests.post 发送到你的钉钉/Telegram/企业微信