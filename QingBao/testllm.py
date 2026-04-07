import requests
import json
import sys

# ================= 配置区域 =================
# 1. API 地址
# 因为你用了隧道，把远程 8000 映射到了本地 8000，所以这里必须写 localhost
API_URL = "http://localhost:8000/v1/chat/completions"

# 2. 模型名称 (非常重要！)
# 必须和你 AutoDL 服务器上启动 vLLM 时指定的 --model 参数一模一样
# 如果你不确定，去服务器终端看一眼启动命令
MODEL_NAME = "qwen-8b"
# ===========================================

def test_local_connection():
    print("-" * 50)
    print(f"📡 正在尝试连接隧道: {API_URL}")
    print(f"🤖 目标模型名称: {MODEL_NAME}")
    print("-" * 50)

    headers = {
        "Content-Type": "application/json"
    }

    # 构造一个极简的测试请求
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个测试助手。"},
            {"role": "user", "content": "如果你收到了这条消息，请只回复'连接成功'这四个字。"}
        ],
        "temperature": 0.7,
        "max_tokens": 20,
        "extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": False  # Python 中 False 首字母大写
            }
        }
    }

    try:
        # 发送请求
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("\n✅ 【测试通过】服务器响应正常！")
            print(f"📝 模型回复内容: {content}")
            print("-" * 50)
            return True
        else:
            print(f"\n❌ 【连接通了，但 API 报错】状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            print("💡 建议：检查 MODEL_NAME 是否和服务器启动参数一致。")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ 【连接失败】无法连接到 localhost:8000")
        print("🔍 排查思路：")
        print("1. 你的 SSH 隧道挂了吗？(黑窗口是否还开着？)")
        print("2. 你的 AutoDL 服务器上 vLLM 跑起来了吗？")
        print("3. 隧道映射的端口对吗？是 8000:localhost:8000 吗？")
        return False
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        return False

if __name__ == "__main__":
    test_local_connection()

# python -m vllm.entrypoints.openai.api_server \
#     --model /root/.cache/modelscope/hub/models/Qwen/Qwen3-8B \
#     --served-model-name qwen-8b \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --tensor-parallel-size 1 \
#     --trust-remote-code \
#     --max-model-len 32768 \
#     --gpu-memory-utilization 0.95
# ssh -CNg -L 8000:127.0.0.1:8000 -p 10041 root@connect.bjb1.seetacloud.com
# ssh -p 10041 root@connect.bjb1.seetacloud.com
# S9SQ6dNTiCWH
#conda activate qb