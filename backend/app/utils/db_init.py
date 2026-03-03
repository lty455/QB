import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库连接配置
config = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT')),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'db': os.getenv('MYSQL_DB'),
    'charset': 'utf8mb4'
}

def init_database():
    """初始化优化后的数据库表"""
    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    # 1. 创建websites表（核心，覆盖所有JSON字段）
    create_website_table = """
    CREATE TABLE IF NOT EXISTS websites (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(512) NOT NULL UNIQUE,
        domain VARCHAR(256) NOT NULL,
        category VARCHAR(128) NOT NULL,
        status ENUM('待抓取', '爬取中', '已完成', '失败') DEFAULT '待抓取',
        last_crawl DATETIME NULL,
        total_pages INT DEFAULT 0,
        error TEXT NULL,
        progress FLOAT DEFAULT 0.0,
        is_active TINYINT DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    # 2. 创建crawl_file_record表（细化文件存储+清洗标记）
    create_crawl_file_table = """
    CREATE TABLE IF NOT EXISTS crawl_file_record (
        id INT AUTO_INCREMENT PRIMARY KEY,
        website_id INT NOT NULL,
        file_path VARCHAR(512) NOT NULL,
        page_num INT DEFAULT 1,
        file_size BIGINT DEFAULT 0,
        crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_cleaned TINYINT DEFAULT 0,
        cleaned_time DATETIME NULL,
        FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE,
        # 联合索引：便于按网站+页码查询文件
        INDEX idx_website_page (website_id, page_num)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    try:
        cursor.execute(create_website_table)
        cursor.execute(create_crawl_file_table)
        conn.commit()
        print("优化后数据库表初始化成功！")
    except Exception as e:
        conn.rollback()
        print(f"初始化失败：{e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()