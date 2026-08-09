"""
宠迹 PawTrack — pytest 配置

说明：
- 纯逻辑测试（JWT、枚举）无需任何外部依赖，可直接运行。
- API 集成测试需要 PostgreSQL + Redis，通过环境变量 PAWTRACK_TEST_DB=1 启用；
  未设置时自动跳过，避免在无基础设施环境下报错。
"""
import os
import sys
import pytest

# 确保 backend 包在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 注册自定义 mark，避免警告
pytest_plugins: list = []


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: 需要数据库/Redis 的集成测试")

# 是否启用需要数据库/Redis 的集成测试
RUN_INTEGRATION = os.environ.get("PAWTRACK_TEST_DB") == "1"


def pytest_collection_modifyitems(config, items):
    """为标记 integration 的用例在无 DB 时自动跳过"""
    skip_integration = pytest.mark.skip(reason="需要 PAWTRACK_TEST_DB=1 及可用数据库/Redis")
    for item in items:
        if "integration" in item.keywords and not RUN_INTEGRATION:
            item.add_marker(skip_integration)
