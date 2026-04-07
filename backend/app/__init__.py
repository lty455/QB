from flask import Flask
from flask_cors import CORS
from app.blueprints.websites import websites_bp
from app.blueprints.crawl import crawl_bp
from app.blueprints.file_scan import file_scan_bp
def create_app():
    app = Flask(__name__)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(websites_bp)
    app.register_blueprint(crawl_bp)
    app.register_blueprint(file_scan_bp)
    return app