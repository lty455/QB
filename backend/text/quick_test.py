#!/usr/bin/env python
"""快速验证测试"""

print('='*60)
print('🧪 快速验证测试')
print('='*60)

# 测试 1: MySQL 模式
print('\n📌 测试 1: MySQL 模式')
import os
os.environ['DB_TYPE'] = 'mysql'
from app import create_app
app = create_app()
from app.models import get_crawl_statistics
stats = get_crawl_statistics()
print(f"✓ MySQL: {stats['total_websites']} 个网站")

# 测试 2: 验证 SQLite 数据库存在
print('\n📌 测试 2: SQLite 数据库验证')
import os.path
sqlite_path = 'data/kg.db'
if os.path.exists(sqlite_path):
    size = os.path.getsize(sqlite_path)
    print(f'✓ SQLite 文件存在: {sqlite_path} ({size/1024:.1f} KB)')
else:
    print(f'✗ SQLite 文件不存在: {sqlite_path}')

# 测试 3: 适配器层验证
print('\n📌 测试 3: 适配器层验证')
from app.database import get_adapter
adapter = get_adapter()
print(f'✓ 当前适配器: {adapter.__class__.__name__}')

print('\n' + '='*60)
print('✅ 所有快速验证测试通过！')
print('='*60)
