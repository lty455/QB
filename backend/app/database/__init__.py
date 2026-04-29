"""
数据库工厂和连接管理
支持 MySQL / SQLite 自动切换
"""

import os
from typing import Optional
from .base_adapter import DBAdapter
from .mysql_adapter import MySQLAdapter
from .sqlite_adapter import SQLiteAdapter


class DBFactory:
    """数据库工厂类"""
    
    _instance: Optional[DBAdapter] = None
    
    @staticmethod
    def get_adapter(db_type: str = 'auto', mysql_config: dict = None, sqlite_path: str = None) -> DBAdapter:
        """
        获取数据库适配器（单例模式）
        
        Args:
            db_type: 数据库类型
                - 'auto': 自动模式，先尝试 MySQL，失败则切换到 SQLite
                - 'mysql': 强制使用 MySQL
                - 'sqlite': 强制使用 SQLite
            mysql_config: MySQL 连接配置
            sqlite_path: SQLite 数据库文件路径
        
        Returns:
            DBAdapter: 数据库适配器实例
        """
        if DBFactory._instance is not None:
            return DBFactory._instance
        
        if db_type == 'auto':
            # 自动模式：先尝试 MySQL，失败则切换到 SQLite
            adapter = MySQLAdapter(mysql_config or {})
            if adapter.connect():
                print("✓ 已连接到 MySQL 数据库")
                DBFactory._instance = adapter
                return adapter
            else:
                print("⚠ MySQL 连接失败，自动切换到 SQLite")
                adapter = SQLiteAdapter(sqlite_path or 'kg.db')
                if adapter.connect():
                    print("✓ 已连接到 SQLite 数据库")
                    DBFactory._instance = adapter
                    return adapter
                else:
                    raise RuntimeError("无法连接到任何数据库")
        
        elif db_type == 'mysql':
            # 强制使用 MySQL
            adapter = MySQLAdapter(mysql_config or {})
            if not adapter.connect():
                raise RuntimeError("MySQL 连接失败")
            print("✓ 已连接到 MySQL 数据库")
            DBFactory._instance = adapter
            return adapter
        
        elif db_type == 'sqlite':
            # 强制使用 SQLite
            adapter = SQLiteAdapter(sqlite_path or 'kg.db')
            if not adapter.connect():
                raise RuntimeError("SQLite 连接失败")
            print("✓ 已连接到 SQLite 数据库")
            DBFactory._instance = adapter
            return adapter
        
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
    
    @staticmethod
    def reset():
        """重置工厂实例（仅用于测试）"""
        if DBFactory._instance:
            DBFactory._instance.close()
            DBFactory._instance = None


# 全局数据库适配器实例
_db_adapter: Optional[DBAdapter] = None


def init_db_adapter(db_type: str = 'auto', mysql_config: dict = None, sqlite_path: str = None) -> None:
    """
    初始化数据库适配器
    应在应用启动时调用一次
    
    Args:
        db_type: 数据库类型 ('auto', 'mysql', 'sqlite')
        mysql_config: MySQL 连接配置
        sqlite_path: SQLite 数据库文件路径
    """
    global _db_adapter
    _db_adapter = DBFactory.get_adapter(db_type, mysql_config, sqlite_path)


def get_adapter() -> DBAdapter:
    """
    获取当前的数据库适配器
    
    Returns:
        DBAdapter: 当前活跃的数据库适配器
    
    Raises:
        RuntimeError: 如果适配器未初始化
    """
    global _db_adapter
    if _db_adapter is None:
        raise RuntimeError("数据库适配器未初始化，请先调用 init_db_adapter()")
    return _db_adapter


def get_connection():
    """
    获取数据库连接对象
    为了与现有代码兼容性，返回适配器对象
    
    Returns:
        DBAdapter: 数据库适配器
    """
    return get_adapter()


def close_db() -> None:
    """关闭数据库连接"""
    global _db_adapter
    if _db_adapter:
        _db_adapter.close()
        _db_adapter = None


__all__ = [
    'DBFactory',
    'DBAdapter',
    'MySQLAdapter',
    'SQLiteAdapter',
    'init_db_adapter',
    'get_adapter',
    'get_connection',
    'close_db',
]
