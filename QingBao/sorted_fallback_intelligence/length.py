import os
import json

# 指定要读取的文件目录（当前目录），你可以修改为实际路径
folder_path = "."

# 遍历目录下的所有文件
for filename in os.listdir(folder_path):
    # 拼接完整文件路径
    file_path = os.path.join(folder_path, filename)

    # 只处理文件（排除文件夹），这里可以根据需要过滤文件类型（如只处理.json）
    if os.path.isfile(file_path):
        try:
            # 读取文件内容（根据文件类型选择读取方式，这里以JSON文件为例，通用文件用read()）
            with open(file_path, 'r', encoding='utf-8') as f:
                # 如果是JSON文件，加载为数据对象；如果是普通文本，直接读字符串
                try:
                    data = json.load(f)  # JSON文件：解析为字典/列表
                except json.JSONDecodeError:
                    f.seek(0)  # 重置文件指针
                    data = f.read()  # 非JSON文件：读取为字符串

            # 计算数据长度（len(data)）
            data_length = len(data)

            # 按格式输出：文件名: 长度
            print(f"{filename}: {data_length}")

        except Exception as e:
            # 处理读取失败的情况（如权限问题、编码错误）
            print(f"{filename}: 读取失败 - {str(e)}")