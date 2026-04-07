import os
import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ================= 配置区域 =================
# 输入根目录 (会自动扫描所有子文件夹下的 fallback 目录)
INPUT_DIR = "../backend/data/websites"

# 输出文件夹 (专属 fallback 的输出)
OUTPUT_DIR = "./sorted_fallback_intelligence"

API_URL = "http://localhost:8000/v1/chat/completions"
API_KEY = "EMPTY"
MODEL_NAME = "qwen-8b"  # 确保和你的 vLLM 启动参数一致

MAX_WORKERS = 10
# ===========================================

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ================= 实体库定义 (战略级+泛化武器) =================
ENTITY_DB = {
    "TIER_1_STRATEGIC": [
        {"name": "Vladimir Putin", "aliases": ["putin", "vladimir putin", "普京"]},
        {"name": "Volodymyr Zelenskyy", "aliases": ["zelenskyy", "zelensky", "泽连斯基"]},
        {"name": "Joe Biden", "aliases": ["biden", "potus", "拜登", "白宫"]},
        {"name": "Donald Trump", "aliases": ["donald trump", "trump", "特朗普", "川普"]},
        {"name": "Xi Jinping", "aliases": ["xi jinping", "习近平", "中南海"]},
        {"name": "Benjamin Netanyahu", "aliases": ["netanyahu", "内塔尼亚胡"]},
        {"name": "Ali Khamenei", "aliases": ["khamenei", "supreme leader of iran", "哈梅内伊"]},
        {"name": "Kim Jong Un", "aliases": ["kim jong un", "金正恩"]},
        {"name": "Yahya Sinwar", "aliases": ["sinwar", "辛瓦尔"]},
        {"name": "Lloyd Austin", "aliases": ["lloyd austin", "secdef", "奥斯汀", "美防长"]},
        {"name": "Sergei Shoigu", "aliases": ["shoigu", "绍伊古"]},
        {"name": "NATO", "aliases": ["nato", "北约", "北大西洋公约组织"]},
        {"name": "US CENTCOM", "aliases": ["centcom", "uscentcom", "中央司令部"]},
        {"name": "US INDOPACOM", "aliases": ["indopacom", "印太司令部"]},
        {"name": "IRGC", "aliases": ["irgc", "islamic revolutionary guard corps", "伊斯兰革命卫队", "革命卫队"]},
        {"name": "Mossad", "aliases": ["mossad", "摩萨德"]},
        {"name": "CIA", "aliases": ["cia", "中情局"]},
        {"name": "FSB/GRU", "aliases": ["fsb", "gru", "俄罗斯联邦安全局", "格鲁乌"]},
        {"name": "Taiwan Strait", "aliases": ["taiwan strait", "台湾海峡", "台海"]},
        {"name": "Strait of Hormuz", "aliases": ["strait of hormuz", "hormuz", "霍尔木兹"]},
        {"name": "Red Sea / Bab el-Mandeb", "aliases": ["red sea", "bab el-mandeb", "红海", "曼德海峡"]},
        {"name": "South China Sea", "aliases": ["south china sea", "南海", "仁爱礁", "黄岩岛"]},
        {"name": "Suwałki Gap", "aliases": ["suwalki gap", "苏瓦乌基走廊"]},
        {"name": "Korean Peninsula", "aliases": ["korean peninsula", "38th parallel", "朝鲜半岛", "三八线"]},
        {"name": "Natanz/Fordow", "aliases": ["natanz", "fordow", "纳坦兹", "福尔多"]},
        {"name": "Nuclear Assets",
         "aliases": ["nuclear", "uranium", "plutonium", "tactical nuke", "核武器", "核弹", "浓缩铀", "战术核武器"]},
        {"name": "ICBM / Strategic Missile",
         "aliases": ["icbm", "minuteman", "sarmat", "dongfeng", "洲际导弹", "弹道导弹", "民兵3", "萨尔马特", "东风"]},
        {"name": "Hypersonic Weapon",
         "aliases": ["hypersonic", "hgv", "kinzhal", "zircon", "高超音速", "高超声速", "匕首导弹", "皓石"]},
        {"name": "Space Warfare / ASAT",
         "aliases": ["anti-satellite", "asat", "space force", "太空武器", "反卫星", "太空军"]},
        {"name": "Strategic Nuclear Submarine", "aliases": ["ssbn", "boomer", "ohio class", "战略核潜艇"]},
        {"name": "Military Chip Export Control",
         "aliases": ["chip export control", "tsmc sanction", "military semiconductor", "芯片禁令", "出口管制",
                     "军用芯片", "光刻机禁运"]},
        {"name": "Rare Earth Elements", "aliases": ["rare earth", "gallium", "germanium", "稀土", "镓", "锗"]},
        {"name": "Critical Cyberattack", "aliases": ["cyberattack", "power grid hack", "国家级网络攻击", "电网瘫痪"]}
    ],
    "TIER_2_TACTICAL": [
        {"name": "Gaza Strip / Rafah", "aliases": ["gaza", "rafah", "加沙", "拉法"]},
        {"name": "Black Sea", "aliases": ["black sea", "黑海", "克里米亚"]},
        {"name": "Defense Contractors",
         "aliases": ["lockheed martin", "raytheon", "boeing defense", "洛克希德马丁", "雷神公司", "波音防务"]},
        {"name": "Armed Groups",
         "aliases": ["houthi", "hezbollah", "hamas", "胡塞", "真主党", "哈马斯", "瓦格纳", "雇佣兵"]},
        {"name": "Fighter Jet",
         "aliases": ["fighter jet", "stealth fighter", "f-35", "f-16", "f-22", "su-35", "j-20", "战斗机", "隐身战机",
                     "歼击机"]},
        {"name": "Strategic Bomber", "aliases": ["bomber", "b-52", "b-2", "b-21", "轰炸机", "战略轰炸机"]},
        {"name": "Air Defense & Interceptors",
         "aliases": ["air defense", "iron dome", "patriot", "s-400", "thaad", "防空系统", "铁穹", "爱国者", "萨德"]},
        {"name": "Unmanned Aerial Vehicle (UAV)",
         "aliases": ["uav", "drone", "fpv", "loitering munition", "shahed", "mq-9", "无人机", "穿越机", "巡飞弹",
                     "自杀式无人机"]},
        {"name": "Unmanned Naval Vehicle (USV)", "aliases": ["sea drone", "usv", "uuv", "无人艇", "无人水面载具"]},
        {"name": "Electronic Warfare (EW)",
         "aliases": ["electronic warfare", "jamming", "gps spoofing", "电子战", "信号干扰", "电磁压制"]},
        {"name": "Directed Energy Weapon",
         "aliases": ["directed energy", "laser weapon", "dragonfire", "iron beam", "定向能", "激光武器", "铁束"]},
        {"name": "Smart Munitions", "aliases": ["glide bomb", "umpk", "jdam", "滑翔炸弹", "精确制导炸弹"]}
    ]
}


def build_fuzzy_pattern(alias):
    alias = alias.lower().strip()
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', alias))
    pattern_str = re.sub(r'[-\s]+', r'[- ]?', alias)
    pattern_str = pattern_str.replace("(", r"\(").replace(")", r"\)")

    if has_chinese:
        return pattern_str
    else:
        return rf"\b{pattern_str}(?:s|es)?\b"


def scan_entities(text):
    text_lower = text.lower()
    matched = []

    for tier, entities in ENTITY_DB.items():
        tier_label = "Tier 1" if "TIER_1" in tier else "Tier 2"
        for ent in entities:
            entity_matched = False
            for alias in ent["aliases"]:
                pattern = build_fuzzy_pattern(alias)
                if re.search(pattern, text_lower):
                    entity_matched = True
                    break
            if entity_matched:
                matched.append(f"{ent['name']} ({tier_label})")

    matched = list(set(matched))
    return ", ".join(matched) if matched else "None"


def detect_language(title, text):
    sample = (str(title) + str(text))[:200]
    if re.search(r'[\u4e00-\u9fff]', sample): return "zh"
    return "en"


def validate_article(data):
    title = data.get("title", "")
    text = data.get("text", "")

    if isinstance(title, list) and not title: title = ""
    if isinstance(text, list) and not text: text = ""

    title_str = str(title).strip()
    text_str = str(text).strip()

    if not title_str or not text_str: return False, None, None
    if title_str == "[]" or text_str == "[]": return False, None, None
    if "404 Not Found" in title_str or "404 Not Found" in text_str: return False, None, None

    return True, title_str, text_str


def get_prompt(title, text, source, date, lang, matched_entities):
    short_text = text[:2500]
    user_content = f"Source (Authority check): {source}\nDate (Timeliness check): {date}\nTitle: {title}\nMatched Entities (Attention check): [{matched_entities}]\nContent:\n{short_text}"

    if lang == "zh":
        system_prompt = """你是一个极其严苛的军工与战略情报评估系统。
任务：严格根据【漏斗与矩阵双重评估法】，对输入情报的“军事情报价值”打分(0-100)。

【⚠️第一层漏斗：相关度一票否决 (决定及格线)】
本系统只为“军工科技、武装冲突、地缘安全”服务。
如果文章的主题是：普通股市大盘、纯粹的商业财报分析（即使涉及军工企业股票跳水）、民用科技（如消费电子）、国内社会新闻、体育娱乐等，无论其数据多么详实、来源多么权威，【最高只能给 59 分】。绝不允许逾越！

【✅第二层矩阵：六维数据评估 (决定 60分以上高度)】
核心主题为：军事行动、武器实战/研发、军队调动、战略供应链断供、地缘冲突时，才允许打 60 分以上。此后根据以下维度加分：
1. 权威性：来源是否官方/主流媒体？
2. 关注度：是否涉及【Matched Entities】中的战略/战术目标？
3. 时效性：是否为最新事件？
4. 准确性：行文是否客观中立？（情绪宣泄、阴谋论大幅扣分）。
5. 完整性(核心)：是否包含具体的 5W1H（精确时间、坐标、具体的武器型号参数、部队番号、确切数据）？

【综合评分量表】
- 90-100分 (顶级军事情报)：六维拉满。权威发布，涉及高敏感实体且包含极度详实的战术参数/部署细节（完整性极高），客观准确。
- 70-89分 (高价值军事数据)：明确的军事行动、武器测试、精确打击战报。数据客观且要素齐全（包含型号、数据、地点）。
- 60-69分 (及格军事资讯)：泛泛而谈的国防政策、例行军演简讯、无具体细节的安全抗议（完整性一般）。
- 30-59分 (跨界/低质噪音)：所有【股市/纯商业/民用科技】报道（触发一票否决），或主题是军事但来源不明、毫无细节的空洞文章。
- 0-29分 (纯垃圾)：广告、体育、娱乐、404报错。

【输出要求】
仅输出 JSON，格式：{"score": int}
严禁输出 Markdown 标记或解释！"""

    else:
        system_prompt = """You are a strictly rigorous Military & Strategic Intelligence Evaluation System.
Task: Assess "Military Intelligence Value" (0-100) based on a 【Funnel + Matrix Dual Evaluation Method】.

【⚠️ First Funnel: The Relevance Veto (The 60-Point Ceiling)】
Strictly serves "Military Tech, Armed Conflicts, Geopolitical Security".
If primary topic is: General stock market, pure corporate earnings (even for defense contractors), civilian tech, domestic news, sports, entertainment... 
Regardless of authority or data completeness, 【THE SCORE MUST NOT EXCEED 59】.

【✅ Second Matrix: The 6-Dimensional Evaluation (Scoring > 60)】
Only when core subject is indisputably: Military ops, weapon R&D/combat, troop movements, supply chain embargoes, or geopolitical conflicts.
Once past 60, rank higher based on:
1. Authoritativeness: Official agency or recognized media?
2. Attention: Deeply involves high-value [Matched Entities]?
3. Timeliness: Recent/breaking event?
4. Accuracy (Objectivity): Objective, neutral, fact-based tone? (Propaganda/emotional rants lose points).
5. Completeness (CRUCIAL): Are all data elements present? Contains specific 5W1H details (exact coordinates, weapon parameters, unit designations, precise data)?

【Comprehensive Scoring Scale】
- 90-100 (Top-Tier MILITARY Intel): Excels in all dimensions. Highly sensitive entities with extreme tactical/deployment parameters (Max completeness), strictly objective.
- 70-89 (High-Value MILITARY Data): Concrete military actions, weapon tests, detailed defense procurement. Objective and element-rich (models, numbers, locations).
- 60-69 (Passable MILITARY Info): Vague defense policies, brief notices of routine drills, protests lacking specific details.
- 30-59 (Off-Topic / Low Quality): ALL 【Stock Market / Pure Corporate Finance / Civilian Tech】 reports (Veto triggered), OR military-related articles completely lacking factual details/authority.
- 0-29 (Junk): Ads, sports, entertainment, 404 errors.

【Output Requirement】
Output ONLY JSON format: {"score": int}
NO Markdown or explanations!"""

    return system_prompt, user_content


def call_llm(file_path):
    relative_filename = os.path.relpath(file_path, INPUT_DIR).replace(os.sep, "/")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        is_valid, title, text = validate_article(data)
        if not is_valid: return None

        matched_entities = scan_entities(title + " " + text)
        lang = detect_language(title, text)
        source = data.get("source_domain", "Unknown")
        date = data.get("date_publish", "Unknown")

        sys_prompt, user_msg = get_prompt(title, text, source, date, lang, matched_entities)

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.1,
            "max_tokens": 15,
            "response_format": {"type": "json_object"},
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']

            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
            content = content.replace("```json", "").replace("```", "").strip()

            score_data = json.loads(content)
            score = int(score_data.get("score", 0))

            return {
                "filename": relative_filename,
                "score": score,
                "matched_entities": matched_entities,
                "title": title,
                "url": data.get("url"),
                "date": date
            }
        else:
            print(f"API Error [{relative_filename}]: {response.text}")
            return None

    except Exception as e:
        print(f"Error processing {relative_filename}: {e}")
        return None


def get_interval_name(score):
    score = max(0, min(100, score))
    if score == 100:
        lower = 90
    else:
        lower = (score // 10) * 10
    upper = lower + 10
    return f"{lower}-{upper}.json"


def main():
    all_files = []
    print(f"Scanning directory: {INPUT_DIR} strictly for 'fallback' folders...")

    # 递归扫描
    for root, dirs, files in os.walk(INPUT_DIR):
        # =========================================================
        # 核心修改：判断当前遍历的文件夹名字是不是 "fallback"
        # 只有在 "fallback" 文件夹里的 json 文件才会被加入处理列表
        # =========================================================
        if os.path.basename(root) == "fallback":
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(root, file)
                    all_files.append(full_path)

    if not all_files:
        print("No JSON files found in any 'fallback' directories!")
        return

    print(f"Found {len(all_files)} files in fallback folders. Starting analysis...")

    buckets = {f"{i}-{i + 10}.json": [] for i in range(0, 100, 10)}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(call_llm, f): f for f in all_files}

        for future in tqdm(as_completed(futures), total=len(all_files), desc="Analyzing"):
            result = future.result()
            if result:
                target_file = get_interval_name(result['score'])
                buckets[target_file].append(result)

    print("Writing results...")
    for filename, items in buckets.items():
        if items:
            save_path = os.path.join(OUTPUT_DIR, filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Done! Check the '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()