# app/monitor.py
import sqlite3
import time
import feedparser
from datetime import datetime, timedelta, timezone
import statistics

# 数据库文件路径
DB_PATH = 'traffic_monitor.db'

# 【配置你的 RSS 源列表】
# 建议这里填入你 500 个网站对应的 RSS 链接。
# 很多网站的 RSS 默认是 url/feed 或 url/rss.xml
RSS_FEEDS = [
    "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?max=10&Site=945",  # 示例：美国国防部RSS
    "https://news.usni.org/feed",  # 示例：USNI RSS
    # "https://你的其他网站.com/feed",
]


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


def fetch_recent_rss_count():
    """极速拉取所有 RSS，统计过去 15 分钟内的新增文章数"""
    new_articles_count = 0

    # 获取 15 分钟前的 UTC 时间（因为 RSS 通常使用 UTC）
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=15)

    for rss_url in RSS_FEEDS:
        try:
            # feedparser 解析极快，几乎不耗资源
            feed = feedparser.parse(rss_url)

            for entry in feed.entries:
                # 解析 RSS 中的发布时间
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)

                    # 如果发布时间在过去 15 分钟内，计数 +1
                    if pub_time >= time_threshold:
                        new_articles_count += 1
        except Exception as e:
            print(f"⚠️ 解析 RSS 失败 {rss_url}: {e}")
            continue

    return new_articles_count


def lightweight_rss_sniff():
    """每 15 分钟执行一次的主监控函数"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 启动轻量级 RSS 流量雷达扫描...")

    # 1. 获取过去 15 分钟的全网上新总数
    current_count = fetch_recent_rss_count()
    print(f"📊 本次扫描：全网过去 15 分钟新增 {current_count} 篇文章")

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