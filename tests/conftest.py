"""
Общие фикстуры для тестов CBT-бота.

Подменяем DB_FILE на временную БД перед импортом cbt_core,
чтобы не трогать продакшен-базу.
"""
import os
import sys
import tempfile

# ----- Патчим DB_FILE до первого импорта cbt_core -----
# Сохраняем себе путь, где будет лежать cbt_core
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

# Создаём временную БД и подменяем DB_FILE прямо в модуле при первом импорте
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")

# Импортируем cbt_core, но сначала подменим DB_FILE через monkeypatch-like подход
# Поскольку cbt_core вычисляет DB_FILE на уровне модуля, сделаем хитрее:
# 1. Создаём временный .env, чтобы load_dotenv не мешался
# 2. Мокаем os.path.join внутри cbt_core

import builtins
_original_join = os.path.join

def _patched_join(*args):
    result = _original_join(*args)
    if "cbt_data.db" in result and not "tmp" in result:
        return _test_db_path
    return result

os.path.join = _patched_join

# Теперь импорт создаст таблицы во временной БД
import cbt_core as core

# Возвращаем оригинальный join (остальное через monkeypatch)
os.path.join = _original_join

# Принудительно инитим БД с тестовым путём
core.DB_FILE = _test_db_path
core.init_db()

import pytest


@pytest.fixture(autouse=True)
def clean_db():
    """Очищаем все таблицы перед каждым тестом."""
    yield
    conn = core.sqlite3.connect(_test_db_path)
    c = conn.cursor()
    c.execute("DELETE FROM cbt_records")
    c.execute("DELETE FROM daily_plans")
    c.execute("DELETE FROM plan_items")
    c.execute("DELETE FROM achievements")
    conn.commit()
    conn.close()


@pytest.fixture
def test_user():
    """Стандартный ID тестового пользователя."""
    return 100500


@pytest.fixture
def admin_user():
    """ID админа."""
    return core.ADMIN_ID


@pytest.fixture
def core_module():
    """Возвращает модуль cbt_core для использования в тестах."""
    return core


def pytest_unconfigure():
    """Удаляем временную БД после всех тестов."""
    import os
    os.close(_test_db_fd)
    try:
        os.unlink(_test_db_path)
    except OSError:
        pass
