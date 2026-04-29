"""
数据库适配器完整测试脚本
验证所有功能是否正常工作
"""

import os
import sys


def test_mysql_mode():
    """测试 MySQL 模式"""
    print("\n" + "="*60)
    print("测试 1: MySQL 模式")
    print("="*60)
    
    os.environ['DB_TYPE'] = 'mysql'
    
    try:
        from app import create_app
        app = create_app()
        
        from app.models import get_crawl_statistics, load_all_websites, get_website_by_id
        
        print("✓ 应用启动成功")
        
        # 测试统计
        stats = get_crawl_statistics()
        print(f"✓ 获取统计信息: {stats['total_websites']} 个网站")
        
        # 测试加载所有网站
        websites = load_all_websites()
        print(f"✓ 加载网站列表: {len(websites)} 个网站")
        
        # 测试单个网站查询
        if websites:
            website_id = websites[0]['id']
            site = get_website_by_id(website_id)
            print(f"✓ 查询单个网站 (ID={website_id}): {site['url'][:50]}...")
        
        print("\n✅ MySQL 模式测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ MySQL 模式测试失败: {e}")
        return False


def test_sqlite_mode():
    """测试 SQLite 模式"""
    print("\n" + "="*60)
    print("测试 2: SQLite 模式")
    print("="*60)
    
    # 重新导入以重置单例
    for module in list(sys.modules.keys()):
        if module.startswith('app'):
            del sys.modules[module]
    
    os.environ['DB_TYPE'] = 'sqlite'
    
    try:
        from app import create_app
        app = create_app()
        
        from app.models import get_crawl_statistics, load_all_websites, get_website_by_id
        
        print("✓ 应用启动成功")
        
        # 测试统计
        stats = get_crawl_statistics()
        print(f"✓ 获取统计信息: {stats['total_websites']} 个网站")
        
        # 测试加载所有网站
        websites = load_all_websites()
        print(f"✓ 加载网站列表: {len(websites)} 个网站")
        
        # 测试单个网站查询
        if websites:
            website_id = websites[0]['id']
            site = get_website_by_id(website_id)
            print(f"✓ 查询单个网站 (ID={website_id}): {site['url'][:50]}...")
        
        print("\n✅ SQLite 模式测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ SQLite 模式测试失败: {e}")
        return False


def test_auto_mode():
    """测试 Auto 模式（自动容错）"""
    print("\n" + "="*60)
    print("测试 3: Auto 模式（MySQL 失败自动切换 SQLite）")
    print("="*60)
    
    # 重新导入以重置单例
    for module in list(sys.modules.keys()):
        if module.startswith('app'):
            del sys.modules[module]
    
    os.environ['DB_TYPE'] = 'auto'
    os.environ['MYSQL_HOST'] = 'invalid-host-12345.local'
    
    try:
        from app import create_app
        app = create_app()
        
        from app.models import get_crawl_statistics
        
        print("✓ 应用启动成功（已自动从 MySQL 切换到 SQLite）")
        
        # 测试统计
        stats = get_crawl_statistics()
        print(f"✓ 获取统计信息: {stats['total_websites']} 个网站")
        
        print("\n✅ Auto 模式测试通过！（自动容错成功）")
        return True
        
    except Exception as e:
        print(f"\n❌ Auto 模式测试失败: {e}")
        return False


def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "="*60)
    print("测试 4: 数据一致性验证")
    print("="*60)
    
    # 重新导入以重置单例
    for module in list(sys.modules.keys()):
        if module.startswith('app'):
            del sys.modules[module]
    
    os.environ['DB_TYPE'] = 'mysql'
    
    try:
        from app import create_app
        app = create_app()
        
        from app.models import get_crawl_statistics as get_stats_mysql
        stats_mysql = get_stats_mysql()
        total_mysql = stats_mysql['total_websites']
        
        print(f"✓ MySQL 数据: {total_mysql} 个网站")
        
        # 重新导入以重置单例
        for module in list(sys.modules.keys()):
            if module.startswith('app'):
                del sys.modules[module]
        
        os.environ['DB_TYPE'] = 'sqlite'
        
        from app import create_app
        app = create_app()
        
        from app.models import get_crawl_statistics as get_stats_sqlite
        stats_sqlite = get_stats_sqlite()
        total_sqlite = stats_sqlite['total_websites']
        
        print(f"✓ SQLite 数据: {total_sqlite} 个网站")
        
        if total_mysql == total_sqlite:
            print(f"\n✅ 数据一致性验证通过！（两个数据库都有 {total_mysql} 条记录）")
            return True
        else:
            print(f"\n⚠️ 数据不一致：MySQL {total_mysql} vs SQLite {total_sqlite}")
            return False
        
    except Exception as e:
        print(f"\n❌ 数据一致性测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 数据库适配器完整测试套件")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("MySQL 模式", test_mysql_mode()))
    results.append(("SQLite 模式", test_sqlite_mode()))
    results.append(("Auto 模式", test_auto_mode()))
    results.append(("数据一致性", test_data_consistency()))
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统已就绪。")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 项测试失败，请检查配置。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
