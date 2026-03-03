from app import create_app
from app.crawler.worker import start_workers

app = create_app()

if __name__ == '__main__':
    # 启动爬虫工作线程（需在 Flask 运行前启动，使用 daemon 线程）
    start_workers(num_workers=3)

    # 运行 Flask 开发服务器，禁用 reloader 以免重复启动线程
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)