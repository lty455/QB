import os
import json
import shutil

# ==================== 核心路径配置（根据截图已固定）====================
# 获取脚本所在的根目录 (kg-platform)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 源目录：原始文章所在文件夹
SRC_WEBSITES_DIR = os.path.join(BASE_DIR, "backend", "data", "websites")

# 分数文件目录
SORTED_DIR = os.path.join(BASE_DIR, "QingBao", "sorted_fallback_intelligence")

# 目标目录：复制后的新文件夹
TARGET_DIR = os.path.join(BASE_DIR, "fallback_60-100")

# 需要处理的分数段
score_files = ["60-70.json", "70-80.json", "80-90.json", "90-100.json"]


# ==================== 逻辑执行 ====================
def main():
    # 校验目录是否存在
    if not os.path.isdir(SRC_WEBSITES_DIR):
        print(f"❌ 错误：源目录不存在 -> {SRC_WEBSITES_DIR}")
        return

    if not os.path.isdir(SORTED_DIR):
        print(f"❌ 错误：分数目录不存在 -> {SORTED_DIR}")
        return

    copied_count = 0

    for score_file in score_files:
        score_path = os.path.join(SORTED_DIR, score_file)
        if not os.path.exists(score_path):
            print(f"⚠️  跳过：分数文件不存在 -> {score_file}")
            continue

        print(f"\n🔍 正在处理 {score_file}...")
        try:
            with open(score_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception as e:
            print(f"❌ 读取 {score_file} 失败: {e}")
            continue

        for article in articles:
            filename = article.get("filename")
            if not filename:
                continue

            # 拼接源文件绝对路径
            src_file_path = os.path.join(SRC_WEBSITES_DIR, filename)
            # 拼接目标文件绝对路径
            dst_file_path = os.path.join(TARGET_DIR, filename)

            if os.path.exists(src_file_path):
                # 创建目标子目录
                os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
                # 复制文件
                shutil.copy2(src_file_path, dst_file_path)
                copied_count += 1
                # 打印详细复制日志（可选，注释掉以提速）
                # print(f"✅ 复制: {filename}")
            # else:
            #     print(f"⚠️  跳过 (源文件不存在): {filename}")

    print(f"\n{'=' * 30}")
    print(f"📊 任务完成！")
    print(f"📍 目标目录: {TARGET_DIR}")
    print(f"📁 成功复制文件数: {copied_count}")


if __name__ == "__main__":
    main()