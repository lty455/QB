"""
MySQL 数据库适配器 (多线程安全版)
实现针对 MySQL 的数据库操作，采用按需连接模式防止并发崩溃
"""

import pymysql
import pymysql.cursors
from typing import Dict, List, Optional
# ⚠️ 注意：这里使用 BaseAdapter 以匹配我们之前定义的基类名
from .base_adapter import DBAdapter


class MySQLAdapter(DBAdapter):
    """MySQL 数据库适配器 (线程安全)"""

    def __init__(self, config: Dict):
        """
        初始化 MySQL 适配器
        Args:
            config: MySQL 连接配置字典
        """
        self.config = config
        # 测试一下配置是否正确，但不保持长连接
        try:
            conn = self._get_connection()
            conn.close()
            print("[MySQL] 适配器初始化成功 (按需连接/线程安全模式)")
        except Exception as e:
            print(f"[MySQL] 初始化失败，请检查配置: {e}")

    def _get_connection(self):
        """核心机制：每次调用生成一个新的、完全独立的连接"""
        return pymysql.connect(
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 3306),
            user=self.config.get('user', 'root'),
            password=self.config.get('password', ''),
            database=self.config.get('db', 'knowledge_graph'), # 兼容你原代码的 'db' 键
            charset=self.config.get('charset', 'utf8mb4'),
            cursorclass=pymysql.cursors.DictCursor
        )

    @staticmethod
    def _convert_placeholders(sql: str) -> str:
        """将 SQLite 风格的 ? 占位符转换为 MySQL 风格的 %s"""
        return sql.replace('?', '%s')

    def connect(self) -> bool:
        """为兼容旧代码保留的方法。短连接模式下无需手动connect"""
        return True

    def close(self) -> None:
        """为兼容旧代码保留的方法。短连接模式下会在方法内自动close"""
        pass

    def execute(self, sql: str, params: tuple = None) -> int:
        """执行单条 INSERT/UPDATE/DELETE (已实现自动提交)"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()  # 短连接必须当场提交
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"[MySQL] 执行失败: {e}")
            return 0
        finally:
            conn.close()  # 用完立刻归还/关闭

    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """执行批量 INSERT/UPDATE/DELETE"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"[MySQL] 批量执行失败: {e}")
            return 0
        finally:
            conn.close()

    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict]:
        """获取单条记录"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return cursor.fetchone()
        except Exception as e:
            print(f"[MySQL] 查询失败: {e}")
            return None
        finally:
            conn.close()

    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict]:
        """获取所有记录"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"[MySQL] 查询失败: {e}")
            return []
        finally:
            conn.close()

    def commit(self) -> None:
        """由于 execute 方法内部已自动提交，这里只需保持 API 兼容即可"""
        pass

    def rollback(self) -> None:
        """同上，异常时已在方法内部自动回滚"""
        pass

    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            sql = "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s"
            # 注意这里直接调用类里的 fetch_one，它会自动走短连接逻辑
            result = self.fetch_one(sql, (self.config.get('db'), table_name))
            return result is not None
        except Exception:
            return False