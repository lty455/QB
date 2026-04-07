from flask import Blueprint, jsonify, abort
import os
import glob
import json

file_scan_bp = Blueprint('file_scan', __name__)

# 计算目标文件夹路径（相对于项目根目录 kg-platform）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# SORTED_INTELLIGENCE_DIR = os.path.join(BASE_DIR, "QingBao", "sorted_intelligence")
SORTED_INTELLIGENCE_DIR=r"C:\Users\24564\PycharmProjects\PythonProject\kg-platform\QingBao\sorted_intelligence"


@file_scan_bp.route('/api/files', methods=['GET'])
def list_files():
    """
    扫描 sorted_intelligence 文件夹，返回所有 0-10.json ... 90-100.json 文件（降序）
    """
    try:
        # 修复匹配规则：支持 xx-xxx.json（90-100.json）和 xx-xx.json（80-90.json）
        file_pattern = os.path.join(SORTED_INTELLIGENCE_DIR, "[0-9]*-[0-9]*.json")
        files = glob.glob(file_pattern)

        if not files:
            return jsonify({"files": []})

        # 提取文件名并按 90-100 → 0-10 降序排序
        file_names = [os.path.basename(f) for f in files]
        # 排序逻辑优化：兼容 90-100、80-90 等格式
        file_names.sort(key=lambda x: -int(x.split("-")[0]))

        return jsonify({"files": file_names})
    except Exception as e:
        return jsonify({"error": f"扫描文件失败: {str(e)}"}), 500


@file_scan_bp.route('/api/files/<filename>', methods=['GET'])
def load_file(filename):
    """
    加载指定 JSON 文件内容
    """
    try:
        file_path = os.path.join(SORTED_INTELLIGENCE_DIR, filename)
        if not os.path.exists(file_path):
            abort(404, description="文件不存在")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"filename": filename, "data": data})
    except Exception as e:
        return jsonify({"error": f"加载文件失败: {str(e)}"}), 500