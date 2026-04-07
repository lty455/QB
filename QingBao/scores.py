import os
import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ================= 配置区域 =================
INPUT_DIR = "../backend/data/websites"
OUTPUT_DIR = "./sorted_intelligence"

API_URL = "http://localhost:8000/v1/chat/completions"
API_KEY = "EMPTY"
MODEL_NAME = "qwen-8b"  # 确保和你的 vLLM 启动参数一致

MAX_WORKERS = 10
# ===========================================

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ================= 实体库定义 (结合最新热点与前沿军事科技) =================
ENTITY_DB = {
    "TIER_1_STRATEGIC": [
        # ----------------------------------------------------------------------
        # 1. 核心决策者与极高价值人物 (High-Value Targets & Decision Makers)
        # ----------------------------------------------------------------------
        {"name": "Vladimir Putin", "aliases": ["putin", "vladimir putin", "普京"]},
        {"name": "Volodymyr Zelenskyy", "aliases": ["zelenskyy", "zelensky", "泽连斯基"]},
        {"name": "Joe Biden", "aliases": ["biden", "potus", "拜登", "白宫"]}, # 虽然是常识，但情报中出现总统直接下令权重极高
        {"name": "Donald Trump", "aliases": ["donald trump", "trump", "特朗普", "川普"]},
        {"name": "Xi Jinping", "aliases": ["xi jinping", "习近平", "中南海"]},
        {"name": "Benjamin Netanyahu", "aliases": ["netanyahu", "内塔尼亚胡", "以总理"]},
        {"name": "Ali Khamenei", "aliases": ["khamenei", "supreme leader of iran", "哈梅内伊", "伊朗最高领袖"]},
        {"name": "Kim Jong Un", "aliases": ["kim jong un", "金正恩"]},
        {"name": "Yahya Sinwar", "aliases": ["sinwar", "辛瓦尔"]}, # 哈马斯现任最高领导人（高危暗杀目标）
        {"name": "Lloyd Austin", "aliases": ["lloyd austin", "secdef", "奥斯汀", "美防长"]},
        {"name": "Sergei Shoigu", "aliases": ["shoigu", "绍伊古"]}, # 俄前防长/现国安会秘书，核心军工负责人

        # ----------------------------------------------------------------------
        # 2. 战略级军事指挥枢纽与情报机构 (Strategic Commands & Intelligence)
        # ----------------------------------------------------------------------
        {"name": "NATO", "aliases": ["nato", "北约", "北大西洋公约组织"]},
        {"name": "US CENTCOM", "aliases": ["centcom", "uscentcom", "中央司令部", "美中央司令部"]},
        {"name": "US INDOPACOM", "aliases": ["indopacom", "印太司令部", "美印太司令部"]},
        {"name": "IRGC", "aliases": ["irgc", "islamic revolutionary guard corps", "伊斯兰革命卫队", "革命卫队"]},
        {"name": "Mossad", "aliases": ["mossad", "摩萨德", "以色列情报特务局"]},
        {"name": "CIA", "aliases": ["cia", "central intelligence agency", "中情局", "美国中央情报局"]},
        {"name": "FSB/GRU", "aliases": ["fsb", "gru", "俄罗斯联邦安全局", "格鲁乌"]}, # 俄情报与特种行动核心

        # ----------------------------------------------------------------------
        # 3. 极高风险地缘咽喉与冲突引爆点 (Chokepoints & Flashpoints)
        # ----------------------------------------------------------------------
        {"name": "Taiwan Strait", "aliases": ["taiwan strait", "台湾海峡", "台海"]},
        {"name": "Strait of Hormuz", "aliases": ["strait of hormuz", "hormuz", "霍尔木兹", "霍尔木兹海峡"]},
        {"name": "Red Sea / Bab el-Mandeb", "aliases": ["red sea", "bab el-mandeb", "红海", "曼德海峡"]},
        {"name": "South China Sea", "aliases": ["south china sea", "南海", "仁爱礁", "黄岩岛"]},
        {"name": "Suwałki Gap", "aliases": ["suwalki gap", "苏瓦乌基走廊"]}, # 北约与俄罗斯的最危险陆地边界
        {"name": "Korean Peninsula", "aliases": ["korean peninsula", "38th parallel", "朝鲜半岛", "三八线"]},
        {"name": "Natanz/Fordow", "aliases": ["natanz", "fordow", "纳坦兹", "福尔多"]}, # 伊朗最核心的地下核设施

        # ----------------------------------------------------------------------
        # 4. 颠覆性技术与大规模杀伤性武器 (Disruptive Tech & WMDs - 概念泛化)
        # ----------------------------------------------------------------------
        {"name": "Nuclear Assets", "aliases": ["nuclear", "uranium", "plutonium", "tactical nuke", "核武器", "核弹", "核武", "浓缩铀", "武器级铀", "战术核武器"]},
        {"name": "ICBM / Strategic Missile", "aliases": ["icbm", "intercontinental ballistic missile", "minuteman", "sarmat", "dongfeng", "洲际导弹", "洲际弹道导弹", "民兵3", "萨尔马特", "东风"]},
        {"name": "Hypersonic Weapon", "aliases": ["hypersonic", "hgv", "kinzhal", "zircon", "avangard", "高超音速", "高超声速", "匕首导弹", "皓石", "先锋导弹"]},
        {"name": "Space Warfare / ASAT", "aliases": ["anti-satellite", "asat", "space force", "orbital weapon", "太空武器", "反卫星", "太空军", "轨道拦截"]},
        {"name": "Strategic Nuclear Submarine", "aliases": ["ssbn", "boomer", "ohio class", "borei class", "战略核潜艇", "弹道导弹核潜艇"]},

        # ----------------------------------------------------------------------
        # 5. 军事科技底座与断供致命节点 (Strategic Supply Chain & Cyber)
        # ----------------------------------------------------------------------
        {"name": "Semiconductor Ban / TSMC", "aliases": ["semiconductor", "tsmc", "chip export control", "asml", "半导体制裁", "芯片禁令", "台积电", "阿斯麦"]},
        {"name": "Rare Earth Elements", "aliases": ["rare earth", "gallium", "germanium", "稀土", "镓", "锗", "出口管制"]},
        {"name": "Critical Cyberattack", "aliases": ["cyberattack", "power grid hack", "infrastructure hack", "国家级网络攻击", "电网瘫痪", "基础设施黑客"]}
    ],

    "TIER_2_TACTICAL": [
        # --- 关键战术地区/战场 ---
        {"name": "Gaza Strip / Rafah", "aliases": ["gaza", "rafah", "加沙", "拉法"]},
        {"name": "Black Sea", "aliases": ["black sea", "黑海", "克里米亚"]},

        # --- 活跃的武装组织 (代理人战争核心) ---
        {"name": "Houthi Movement", "aliases": ["houthi", "houthis", "胡塞"]},
        {"name": "Hezbollah", "aliases": ["hezbollah", "真主党"]},
        {"name": "Hamas", "aliases": ["hamas", "哈马斯"]},
        {"name": "PMC / Mercenaries",
         "aliases": ["wagner", "private military company", "瓦格纳", "雇佣兵", "私人军事公司"]},

        # --- 现代战场高频武器大类 (高度泛化 + 典型型号别名) ---
        {"name": "Fighter Jet",
         "aliases": ["fighter jet", "stealth fighter", "f-35", "f-16", "f-22", "su-35", "j-20", "战斗机", "隐身战机"]},
        {"name": "Strategic Bomber", "aliases": ["bomber", "b-52", "b-21", "tu-160", "轰炸机", "战略轰炸机"]},
        {"name": "Air Defense & Interceptors",
         "aliases": ["air defense", "iron dome", "patriot", "s-400", "防空系统", "铁穹", "爱国者", "拦截系统"]},
        {"name": "Long-Range Strike Missile",
         "aliases": ["cruise missile", "atacms", "storm shadow", "巡航导弹", "战术导弹", "风暴阴影"]},

        # --- 🌟 新兴热点装备 (俄乌/中东战场催生的新形态) ---
        {"name": "Unmanned Aerial Vehicle (UAV)",
         "aliases": ["uav", "drone", "fpv", "loitering munition", "shahed", "无人机", "穿越机", "巡飞弹",
                     "自杀式无人机"]},
        {"name": "Unmanned Naval Vehicle (USV/UUV)",
         "aliases": ["sea drone", "usv", "uuv", "无人艇", "无人水面载具", "水下无人机"]},
        {"name": "Electronic Warfare (EW)",
         "aliases": ["electronic warfare", "jamming", "gps spoofing", "电子战", "信号干扰", "电磁压制"]},
        {"name": "Directed Energy Weapon",
         "aliases": ["directed energy", "laser weapon", "dragonfire", "iron beam", "定向能", "激光武器", "铁束"]},
        {"name": "Smart Munitions", "aliases": ["glide bomb", "umpk", "jdam", "滑翔炸弹", "精确制导炸弹"]}
    ]
}


# ========================================================


def build_fuzzy_pattern(alias):
    """
    根据别名生成高容错的正则表达式模式
    """
    alias = alias.lower().strip()

    # 1. 判断是否包含中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', alias))

    # 2. 处理连字符和空格的变体 (例如 f-35 -> f[- ]?35)
    # 将所有的 - 或空格替换为可选的分隔符正则 [- ]?
    pattern_str = re.sub(r'[-\s]+', r'[- ]?', alias)

    # 转义可能存在的其他正则特殊字符，防止报错
    # 注意: 这里只转义除了我们刚刚构造的 [- ]? 之外的字符，为了简单，通常别名里不会有奇奇怪怪的符号
    # 如果别名里有括号，需要被当成普通字符处理。
    pattern_str = pattern_str.replace("(", r"\(").replace(")", r"\)")

    if has_chinese:
        # 中文不需要单词边界，直接匹配
        return pattern_str
    else:
        # 英文词组需要考虑边界和复数
        # \b 表示单词边界。
        # (?:s|es)? 允许结尾有 s 或 es，应对复数情况 (如 drone -> drones)
        return rf"\b{pattern_str}(?:s|es)?\b"


def scan_entities(text):
    """
    预处理：扫描文本，匹配实体库 (高容错正则版)
    """
    text_lower = text.lower()
    matched = []

    for tier, entities in ENTITY_DB.items():
        tier_label = "Tier 1" if "TIER_1" in tier else "Tier 2"

        for ent in entities:
            entity_matched = False
            for alias in ent["aliases"]:
                # 构建高容错正则
                pattern = build_fuzzy_pattern(alias)

                # 使用正则搜索
                if re.search(pattern, text_lower):
                    entity_matched = True
                    # 一旦该实体的一个别名命中，就跳出别名循环，记录该实体
                    break

            if entity_matched:
                matched.append(f"{ent['name']} ({tier_label})")

    # 去重并返回格式化字符串
    matched = list(set(matched))
    return ", ".join(matched) if matched else "None"

def detect_language(title, text):
    sample = (str(title) + str(text))[:200]
    if re.search(r'[\u4e00-\u9fff]', sample):
        return "zh"
    return "en"


def validate_article(data):
    """验证文章：只读取 title 和 text，处理空值和 404"""
    title = data.get("title", "")
    text = data.get("text", "")  # 严格按照你的要求，只读取 text

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

    # 强化 User Content 的元数据提示
    user_content = f"Source (Authority check): {source}\nDate (Timeliness check): {date}\nTitle: {title}\nMatched Entities (Attention check): [{matched_entities}]\nContent:\n{short_text}"

    if lang == "zh":
        system_prompt = """你是一个极其严苛的军工与战略情报评估系统。
你的任务是严格根据【漏斗与矩阵双重评估法】，对输入情报的“军事情报价值”进行打分(0-100)。

【⚠️第一层漏斗：相关度一票否决 (决定及格线)】
本系统只为“军工科技、武装冲突、地缘安全”服务。
如果文章的主题是：普通股市大盘、纯粹的商业财报分析（即使涉及军工企业股票跳水）、民用科技（如消费电子）、国内社会新闻、体育娱乐等，无论其数据多么详实、来源多么权威，【最高只能给 59 分】。绝不允许逾越！

【✅第二层矩阵：六维数据评估 (决定 60分以上能拿多高)】
只有当核心主题明确为：军事行动、武器装备实战/研发、军队调动、战略供应链断供、地缘冲突时，才允许打 60 分以上。
过了 60 分门槛后，根据以下五个维度决定最终高分：
1. 权威性 (Authoritativeness)：数据来源是否为官方机构、主流媒体或专业智库？（如 .mil, reuters 权威性极高）。
2. 关注度 (Attention)：文章是否深度涉及【Matched Entities】中的高价值战略/战术目标？
3. 时效性 (Timeliness)：是否为最新发生的事件或前瞻性预警？
4. 准确性 (Accuracy)：行文是否客观、中立、基于事实陈述？（情绪化宣泄、主观阴谋论、宣传口号大幅扣分）。
5. 完整性 (Completeness - 核心拉分项)：数据各项要素是否齐全？是否包含具体的 5W1H（精确时间、坐标、具体的武器型号参数、部队番号、确切战果/采购数据）？

【综合评分量表】
- 90-100分 (顶级军事情报)：六维拉满。权威来源的最新发布，涉及高敏感实体且包含极度详实的战术参数/部署细节（完整性极高），客观准确。
- 70-89分 (高价值军事数据)：明确的军事行动、武器测试、精确打击战报、详尽军备采购合同。数据客观且要素齐全（包含型号、数据、地点）。
- 60-69分 (及格军事资讯)：泛泛而谈的国防政策、例行军演简讯、无具体细节的外交安全抗议（完整性一般）。
- 30-59分 (跨界/低质噪音)：包括所有【股市/纯商业/民用科技】的高质量报道（触发一票否决），或者主题是军事但来源不明、毫无细节的空洞文章。
- 0-29分 (纯垃圾)：完全无关的广告、体育、娱乐、404报错。

【输出要求】
仅输出 JSON，格式：{"score": int}
严禁输出 Markdown 标记，严禁输出任何解释！"""

    else:
        system_prompt = """You are a strictly rigorous Military & Strategic Intelligence Evaluation System.
Your task is to assess the "Military Intelligence Value" (0-100) based on a 【Funnel + Matrix Dual Evaluation Method】.

【⚠️ First Funnel: The Relevance Veto (The 60-Point Ceiling)】
This system strictly serves "Military Tech, Armed Conflicts, and Geopolitical Security".
If the article's primary topic is: General stock market/finance, pure corporate earnings reports (even if it's a defense contractor's stock dropping), civilian tech (consumer AI/electronics), domestic societal news, sports, or entertainment... 
Regardless of how authoritative the source or how complete the data is, 【THE SCORE MUST NOT EXCEED 59】. Do not cross this line!

【✅ Second Matrix: The 6-Dimensional Evaluation (Scoring above 60)】
Only when the core subject is indisputably: Military operations, weapon R&D/combat use, troop movements, strategic supply chain embargoes, or geopolitical conflicts, can it score 60 or above.
Once past the 60-point threshold, rank it higher based on these remaining 5 dimensions:
1. Authoritativeness: Is the source an official agency (.mil/.gov), mainstream media, or recognized think tank?
2. Attention (Impact): Does it deeply involve the high-value [Matched Entities]?
3. Timeliness: Is it a recent/breaking event or a forward-looking warning?
4. Accuracy (Objectivity): Is the tone objective, neutral, and fact-based? (Emotional rants, conspiracy theories, or pure propaganda lose significant points).
5. Completeness (CRUCIAL): Are all data elements present? Does it contain specific 5W1H details (exact coordinates, weapon parameters, unit designations, precise casualty/procurement data)?

【Comprehensive Scoring Scale】
- 90-100 (Top-Tier MILITARY Intel): Excels in all dimensions. Authoritative, highly sensitive entities with extreme tactical/deployment parameters (Max completeness), and strictly objective.
- 70-89 (High-Value MILITARY Data): Concrete military actions, weapon tests, precise battle damage assessments, detailed defense procurement contracts. Objective and element-rich (models, numbers, locations).
- 60-69 (Passable MILITARY Info): Vague defense policies, brief notices of routine drills, diplomatic security protests lacking specific details (Average completeness).
- 30-59 (Off-Topic / Low Quality): Includes ALL 【Stock Market / Pure Corporate Finance / Civilian Tech】 reports (Triggering the Veto), OR articles that are military-related but completely lack factual details and authority.
- 0-29 (Junk): Ads, sports, entertainment, 404 errors.

【Output Requirement】
Output ONLY JSON format: {"score": int}
NO Markdown. NO explanations!"""

    return system_prompt, user_content

def call_llm(file_path):
    relative_filename = os.path.relpath(file_path, INPUT_DIR).replace(os.sep, "/")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. 验证文章
        is_valid, title, text = validate_article(data)
        if not is_valid: return None

        # 2. 预扫描实体 (让 Python 做苦力)
        matched_entities = scan_entities(title + " " + text)

        # 3. 构造 Prompt
        lang = detect_language(title, text)
        source = data.get("source_domain", "Unknown")
        date = data.get("date_publish", "Unknown")

        sys_prompt, user_msg = get_prompt(title, text, source, date, lang, matched_entities)

        # 4. 调用 API
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
                "matched_entities": matched_entities,  # 将命中的实体也保存下来，方便你以后在图谱里用
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
    """
    修改为 10分一个区间: 0-10, 10-20, ... 90-100
    """
    score = max(0, min(100, score))
    if score == 100:
        lower = 90
    else:
        lower = (score // 10) * 10

    upper = lower + 10
    return f"{lower}-{upper}.json"


def main():
    all_files = []
    print(f"Scanning directory: {INPUT_DIR} ...")

    for root, dirs, files in os.walk(INPUT_DIR):
        # 跳过 fallback 文件夹
        if "fallback" in dirs:
            dirs.remove("fallback")

        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                all_files.append(full_path)

    if not all_files:
        print("No JSON files found! Please check INPUT_DIR.")
        return

    print(f"Found {len(all_files)} files. Starting analysis...")

    # 初始化 10 个区间桶 (0-10, 10-20 ... 90-100)
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