import os
import requests
import urllib3
import concurrent.futures

# ================= 配置区域 =================
INPUT_FILE = 'urls.txt'  # 存放你原始 URL 的文件，每行一个
OUTPUT_FILE = 'valid_rss.txt'  # 探测成功的 RSS 链接保存位置
TIMEOUT = 5  # 每个请求的超时时间（秒）
MAX_THREADS = 10  # 并发线程数（设置 10-20 跑得比较快）

# 我们要盲猜的常见 RSS 后缀路径
RSS_SUFFIXES = [
    '/feed',
    '/rss',
    '/rss.xml',
    '/feed.xml',
    '/index.xml'
]

# 伪装请求头，防止被反爬虫拦截
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# 禁用由于部分政府/老旧网站 HTTPS 证书过期导致的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================

def test_single_url(original_url):
    """
    测试单个 URL 的所有可能的 RSS 后缀
    如果找到有效的，直接返回该 RSS 链接；否则返回 None
    """
    # 基础清洗：去除空白字符和末尾的斜杠
    base_url = original_url.strip().rstrip('/')

    # 确保有 http 协议头
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url

    for suffix in RSS_SUFFIXES:
        test_url = base_url + suffix
        try:
            # 发起探测请求
            response = requests.get(test_url, headers=HEADERS, timeout=TIMEOUT, verify=False)

            # 如果请求成功
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                # 读取前 200 个字符用于双重校验（防止把普通网页当成 RSS）
                text_start = response.text[:200].lower()

                # 校验条件：Header 声明是 xml/rss，或者源码头部包含 xml/rss 标签
                if 'xml' in content_type or 'rss' in content_type or '<rss' in text_start or '<feed' in text_start or '<?xml' in text_start:
                    return test_url

        except requests.RequestException:
            # 遇到超时、连接错误等，直接跳过测试下一个后缀
            continue

    return None


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到输入文件 '{INPUT_FILE}'，请先创建并填入 URL。")
        return

    # 读取所有 URL
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    total_urls = len(urls)
    print(f"📦 共读取到 {total_urls} 个数据源，开始进行 RSS 盲测探测...\n")

    valid_rss_list = []

    # 使用多线程加速探测
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # 提交所有任务
        future_to_url = {executor.submit(test_single_url, url): url for url in urls}

        count = 0
        for future in concurrent.futures.as_completed(future_to_url):
            original_url = future_to_url[future]
            count += 1

            try:
                found_rss = future.result()
                if found_rss:
                    valid_rss_list.append(found_rss)
                    print(f"[{count}/{total_urls}] ✅ 成功找到: {found_rss}")
                else:
                    print(f"[{count}/{total_urls}] ❌ 未找到: {original_url}")
            except Exception as e:
                print(f"[{count}/{total_urls}] ⚠️ 测试出错 {original_url}: {e}")

    # 将成功的结果写入输出文件
    if valid_rss_list:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for rss in valid_rss_list:
                f.write(rss + '\n')

    # 输出最终统计结果
    print("\n" + "=" * 40)
    print("🎉 探测任务执行完毕！")
    print(f"🎯 原始网站总数 : {total_urls}")
    print(f"✅ 成功找到 RSS : {len(valid_rss_list)} 个")
    print(f"💾 有效 RSS 已保存至 : {OUTPUT_FILE}")
    print("=" * 40)


if __name__ == "__main__":
    main()