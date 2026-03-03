import re

# ---------- 辅助函数 ----------
def extract_domain(url):
    """从URL提取主域名"""
    try:
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        return url.split('/')[0]
    except:
        return ''