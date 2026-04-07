import atexit # 用于注册程序退出时的清理函数
from app import create_app
from app.crawler.worker import start_workers
from app.scheduler import start_scheduler

# === 导入基于 Paramiko 的隧道管理器 ===
from app.utils.tunnel_manager import start_ssh_tunnel, stop_ssh_tunnel

app = create_app()


atexit.register(stop_ssh_tunnel)

if __name__ == '__main__':

    print("\n" + "=" * 50)
    print("🌟 正在启动军工情报自动化工厂...")
    print("=" * 50 + "\n")

    # === 1. 启动 Paramiko SSH 隧道 ===
    # 相比执行系统命令，这种纯 Python 实现不会卡死，且跨平台
    tunnel_success = start_ssh_tunnel()
    if not tunnel_success:
        print("⚠️ 警告：隧道未打通！请检查网络、密码，或本地 8000 端口是否被占用。")
        print("如果隧道不通，明天中午的 LLM 评分任务将报错。")


    # === 【新增 2】启动定时任务调度器 (后台运行，不阻塞主程序) ===
    start_scheduler()
    # 启动爬虫工作线程（需在 Flask 运行前启动，使用 daemon 线程）
    start_workers(num_workers=8)

    # 运行 Flask 开发服务器，禁用 reloader 以免重复启动线程
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)