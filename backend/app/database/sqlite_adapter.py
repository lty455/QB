"""
SQLite 数据库适配器 (多线程安全版)
实现针对 SQLite 的数据库操作，采用按需连接模式防止 Flask 并发崩溃
"""

import sqlite3
from typing import Dict, List, Optional
from .base_adapter import DBAdapter  # 确保导入的是正确的基类名


class SQLiteAdapter(DBAdapter):
    """SQLite 数据库适配器 (线程安全)"""

    def __init__(self, sqlite_path: str):
        """
        初始化 SQLite 适配器
        Args:
            sqlite_path: SQLite 数据库文件路径 (如 ./data/kg.db)
        """
        # 修复刚才报错的核心：必须把传进来的路径存下来！
        self.sqlite_path = sqlite_path

        # 测试一下文件是否可读写，但不保持长连接
        try:
            conn = self._get_connection()
            conn.close()
            print("[SQLite] 适配器初始化成功 (按需连接/线程安全模式)")
        except Exception as e:
            print(f"[SQLite] 初始化失败: {e}")
            raise e

    def _get_connection(self):
        """核心机制：每次调用生成新的独立连接，彻底解决 Flask 多线程报错"""
        # check_same_thread=False 允许不同的 Flask 线程访问
        conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        # 让查询结果可以像字典一样通过列名访问 (完美模拟 MySQL 的 DictCursor)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _convert_placeholders(sql: str) -> str:
        """如果原生的 sql 写的是 MySQL 的 %s，转换为 SQLite 需要的 ?"""
        return sql.replace('%s', '?')

    def connect(self) -> bool:
        """为兼容旧代码保留"""
        return True

    def close(self) -> None:
        """为兼容旧代码保留"""
        pass

    def execute(self, sql: str, params: tuple = None) -> int:
        """执行单条 INSERT/UPDATE/DELETE"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"[SQLite] 执行失败: {e}\nSQL: {sql}")
            return 0
        finally:
            conn.close()

    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """执行批量 INSERT/UPDATE/DELETE"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(sql, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"[SQLite] 批量执行失败: {e}")
            return 0
        finally:
            conn.close()

    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict]:
        """获取单条记录"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            row = cursor.fetchone()
            return dict(row) if row else None  # 转换为标准字典
        except Exception as e:
            print(f"[SQLite] 查询单条失败: {e}")
            return None
        finally:
            conn.close()

    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict]:
        """获取所有记录"""
        sql = self._convert_placeholders(sql)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # 转换为标准字典列表
        except Exception as e:
            print(f"[SQLite] 查询列表失败: {e}")
            return []
        finally:
            conn.close()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def table_exists(self, table_name: str) -> bool:
        """检查 SQLite 表是否存在"""
        try:
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = self.fetch_one(sql, (table_name,))
            return result is not None
        except Exception:
            return False