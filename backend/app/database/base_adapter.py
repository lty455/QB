"""
数据库适配器抽象基类
定义统一的数据库操作接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class DBAdapter(ABC):
    """数据库适配器抽象基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        建立数据库连接
        Returns: True 连接成功，False 连接失败
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def execute(self, sql: str, params: tuple = None) -> int:
        """
        执行 INSERT/UPDATE/DELETE 操作
        Args:
            sql: SQL 语句
            params: 参数元组
        Returns: 受影响的行数
        """
        pass
    
    @abstractmethod
    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """
        批量执行 INSERT/UPDATE/DELETE 操作
        Args:
            sql: SQL 语句
            params_list: 参数元组列表
        Returns: 受影响的总行数
        """
        pass
    
    @abstractmethod
    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict]:
        """
        获取单条记录
        Args:
            sql: SQL 语句
            params: 参数元组
        Returns: 字典格式的记录，或 None
        """
        pass
    
    @abstractmethod
    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict]:
        """
        获取所有记录
        Args:
            sql: SQL 语句
            params: 参数元组
        Returns: 字典格式的记录列表
        """
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """提交事务"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """回滚事务"""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        Args:
            table_name: 表名
        Returns: True 表存在，False 表不存在
        """
        pass
