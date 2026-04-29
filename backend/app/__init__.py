from flask import Flask
from flask_cors import CORS
from app.blueprints.websites import websites_bp
from app.blueprints.crawl import crawl_bp
from app.blueprints.file_scan import file_scan_bp
from app.database import init_db_adapter, close_db
from app.config import DB_TYPE, DB_CONFIG, SQLITE_PATH


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 初始化数据库适配器
    try:
        init_db_adapter(db_type=DB_TYPE, mysql_config=DB_CONFIG, sqlite_path=SQLITE_PATH)
        print(f"[数据库] 已初始化数据库连接 (模式: {DB_TYPE})")
    except Exception as e:
        print(f"[数据库] 初始化失败: {e}")
        raise

    # 注册蓝图
    app.register_blueprint(websites_bp)
    app.register_blueprint(crawl_bp)
    app.register_blueprint(file_scan_bp)
    
    # # 注册应用关闭钩子
    # @app.teardown_appcontext
    # def shutdown_db(exception=None):
    #     close_db()
    
    return app