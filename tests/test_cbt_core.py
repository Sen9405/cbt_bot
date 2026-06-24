"""
Тесты бизнес-логики CBT-бота (cbt_core.py).

Покрытие:
- Форматирование дат (fmt_dt, fmt_date_str, now_str, db_to_display, display_to_db)
- КПТ-записи (save, get, update, delete, count)
- Планы на день (get_or_create_plan, add_plan_item, get_plan_items, toggle, delete)
- Достижения (add, get, delete, update, count, clean_achievement_text)
- Экспорт в Excel (export_to_excel, export_plans_to_excel, export_achievements_to_excel)
- Ограничения FREE (MAX_FREE_RECORDS, MAX_FREE_PLANS, MAX_FREE_ACHIEVEMENTS)
- Форматирование записей (format_record)
- Периоды (get_records_by_period, get_achievements_by_period, get_plans_by_period)
"""
import pytest
from datetime import datetime, date, timedelta


class TestDateFormatters:
    """Форматирование дат."""

    def test_fmt_dt(self, core_module):
        dt = datetime(2026, 6, 17, 13, 30)
        assert core_module.fmt_dt(dt) == "17-06-2026 13:30"

    def test_now_str(self, core_module):
        result = core_module.now_str()
        assert len(result) == 16  # ДД-ММ-ГГГГ ЧЧ:ММ
        assert result[2] == "-" and result[5] == "-"

    def test_fmt_date_str(self, core_module):
        assert core_module.fmt_date_str("2026-06-17") == "17-06-2026"
        assert core_module.fmt_date_str("") == ""
        assert core_module.fmt_date_str("17-06-2026") == "17-06-2026"  # уже в ДД-ММ-ГГГГ

    def test_db_to_display(self, core_module):
        assert core_module.db_to_display("2026-06-17 13:30") == "17-06-2026 13:30"
        assert core_module.db_to_display("") == "-"
        assert core_module.db_to_display(None) == "-"

    def test_display_to_db(self, core_module):
        assert core_module.display_to_db("17-06-2026 13:30") == "2026-06-17 13:30"

    def test_roundtrip(self, core_module):
        """Проверка конвертации туда-обратно."""
        original = datetime(2026, 1, 5, 8, 15)
        display = core_module.fmt_dt(original)
        db = core_module.display_to_db(display)
        assert db == "2026-01-05 08:15"
        back = core_module.db_to_display(db)
        assert back == display


class TestCbtRecords:
    """КПТ-записи."""

    def test_save_and_get(self, core_module, test_user):
        record_id = core_module.save_record(test_user, {
            "situation": "Ссора с коллегой",
            "thought": "Я всё испортил",
            "emotion": "Вина, тревога",
        })
        assert record_id == 1

        records = core_module.get_records(test_user, days=30)
        assert len(records) == 1
        r = records[0]
        assert r[0] == 1  # id
        assert r[1] == test_user
        assert r[3] == "Ссора с коллегой"
        assert r[4] == "Я всё испортил"
        assert r[5] == "Вина, тревога"

    def test_multiple_records_increment_ids(self, core_module, test_user):
        id1 = core_module.save_record(test_user, {"situation": "Первая"})
        id2 = core_module.save_record(test_user, {"situation": "Вторая"})
        id3 = core_module.save_record(test_user, {"situation": "Третья"})
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_save_all_fields(self, core_module, test_user):
        core_module.save_record(test_user, {
            "situation": "Ситуация",
            "thought": "Мысль",
            "emotion": "Эмоция",
            "body_reaction": "Тело",
            "behavior_reaction": "Поведение",
            "confirmation": "Подтверждение",
            "refutation": "Опровержение",
        })
        records = core_module.get_records(test_user, days=30)
        assert len(records) == 1
        r = records[0]
        assert r[3] == "Ситуация"
        assert r[4] == "Мысль"
        assert r[5] == "Эмоция"
        assert r[6] == "Тело"
        assert r[7] == "Поведение"
        assert r[8] == "Подтверждение"
        assert r[9] == "Опровержение"

    def test_get_record_by_id(self, core_module, test_user):
        core_module.save_record(test_user, {"situation": "Тест"})
        record = core_module.get_record_by_id(1, test_user)
        assert record is not None
        assert record[3] == "Тест"

        # Чужой id
        assert core_module.get_record_by_id(999, test_user) is None

    def test_update_record(self, core_module, test_user):
        core_module.save_record(test_user, {"situation": "Старая", "thought": "Старая мысль"})
        core_module.update_record(1, test_user, "situation", "Новая")
        record = core_module.get_record_by_id(1, test_user)
        assert record[3] == "Новая"
        assert record[4] == "Старая мысль"  # не изменилось

    def test_update_invalid_field(self, core_module, test_user):
        core_module.save_record(test_user, {"situation": "Тест"})
        with pytest.raises(ValueError, match="Недопустимое поле"):
            core_module.update_record(1, test_user, "hacked_field", "value")

    def test_delete_record(self, core_module, test_user):
        core_module.save_record(test_user, {"situation": "Будет удалено"})
        assert len(core_module.get_records(test_user, days=30)) == 1
        core_module.delete_record(1, test_user)
        assert len(core_module.get_records(test_user, days=30)) == 0

    def test_delete_other_user_record(self, core_module, test_user):
        """Нельзя удалить запись другого пользователя."""
        other_user = 200500
        core_module.save_record(test_user, {"situation": "Моё"})
        core_module.delete_record(1, other_user)  # не удалится
        assert len(core_module.get_records(test_user, days=30)) == 1

    def test_get_records_count(self, core_module, test_user):
        assert core_module.get_records_count(test_user) == 0
        core_module.save_record(test_user, {"situation": "1"})
        core_module.save_record(test_user, {"situation": "2"})
        assert core_module.get_records_count(test_user) == 2

    def test_get_records_by_period(self, core_module, test_user):
        """Сохранённая запись должна попадать в период."""
        core_module.save_record(test_user, {"situation": "Сегодня"})
        today = date.today()
        week_ago = today - timedelta(days=7)
        next_week = today + timedelta(days=7)
        records = core_module.get_records_by_period(test_user, week_ago, next_week)
        assert len(records) == 1

        # В прошлом году — пусто
        last_year = date(today.year - 1, 1, 1)
        long_ago = date(today.year - 1, 6, 1)
        assert len(core_module.get_records_by_period(test_user, last_year, long_ago)) == 0

    def test_separate_users(self, core_module, test_user):
        """Записи разных пользователей не пересекаются."""
        user_a = 100
        user_b = 200
        core_module.save_record(user_a, {"situation": "A record"})
        core_module.save_record(user_b, {"situation": "B record"})
        core_module.save_record(user_b, {"situation": "B record 2"})

        a_records = core_module.get_records(user_a, days=30)
        b_records = core_module.get_records(user_b, days=30)

        assert len(a_records) == 1
        assert len(b_records) == 2

    def test_max_free_records_limit(self, core_module, test_user, admin_user):
        """Проверяем константу лимита."""
        # Админ не затронут
        assert core_module.MAX_FREE_RECORDS == 20


class TestDailyPlans:
    """Планы на день."""

    def test_get_or_create(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        assert plan_id > 0
        # Повторный вызов возвращает тот же план
        plan_id2 = core_module.get_or_create_plan(test_user, "2026-06-17")
        assert plan_id == plan_id2

    def test_auto_date(self, core_module, test_user):
        """Без указания даты — сегодня."""
        plan_id = core_module.get_or_create_plan(test_user)
        assert plan_id > 0

    def test_add_and_get_items(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        core_module.add_plan_item(plan_id, "Купить молоко")
        core_module.add_plan_item(plan_id, "Сделать зарядку")

        items = core_module.get_plan_items(plan_id)
        assert len(items) == 2
        assert items[0][1] == "Купить молоко"
        assert items[0][2] == 0  # not done
        assert items[1][1] == "Сделать зарядку"

    def test_toggle_item(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        core_module.add_plan_item(plan_id, "Задача")
        items = core_module.get_plan_items(plan_id)
        item_id = items[0][0]

        core_module.toggle_plan_item(item_id)
        items = core_module.get_plan_items(plan_id)
        assert items[0][2] == 1  # done

        core_module.toggle_plan_item(item_id)
        items = core_module.get_plan_items(plan_id)
        assert items[0][2] == 0  # back to not done

    def test_delete_item(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        core_module.add_plan_item(plan_id, "Задача")
        items = core_module.get_plan_items(plan_id)
        assert len(items) == 1

        core_module.delete_plan_item(items[0][0])
        assert len(core_module.get_plan_items(plan_id)) == 0

    def test_delete_plan(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        core_module.add_plan_item(plan_id, "Пункт 1")
        core_module.add_plan_item(plan_id, "Пункт 2")
        core_module.delete_plan(plan_id)
        # После удаления плана пунктов быть не должно
        assert core_module.get_plan_items(plan_id) == []
        assert core_module.count_user_plans(test_user) == 0

    def test_check_plan_exists(self, core_module, test_user):
        exists, has_items = core_module.check_plan_exists(test_user, "2026-06-17")
        assert exists is None
        assert has_items is False

        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        exists, has_items = core_module.check_plan_exists(test_user, "2026-06-17")
        assert exists == plan_id
        assert has_items is False  # пока нет пунктов

        core_module.add_plan_item(plan_id, "Дело")
        exists, has_items = core_module.check_plan_exists(test_user, "2026-06-17")
        assert has_items is True

    def test_get_user_plans(self, core_module, test_user):
        from datetime import date, timedelta
        today = date.today()
        d1 = (today - timedelta(days=2)).isoformat()  # 2 дня назад
        d2 = (today - timedelta(days=1)).isoformat()  # 1 день назад
        core_module.get_or_create_plan(test_user, d1)
        core_module.get_or_create_plan(test_user, d2)
        plans = core_module.get_user_plans(test_user, days=7)
        assert len(plans) >= 2

    def test_get_plans_by_period(self, core_module, test_user):
        core_module.get_or_create_plan(test_user, "2026-06-15")
        core_module.get_or_create_plan(test_user, "2026-06-17")

        start = date(2026, 6, 1)
        end = date(2026, 6, 30)
        result = core_module.get_plans_by_period(test_user, start, end)
        assert len(result) == 2

        # Период без планов
        result = core_module.get_plans_by_period(test_user, date(2020, 1, 1), date(2020, 1, 31))
        assert len(result) == 0


class TestAchievements:
    """Достижения."""

    def test_add_and_get(self, core_module, test_user):
        core_module.add_achievement(test_user, "Пробежал 5 км")
        achievements = core_module.get_user_achievements(test_user)
        assert len(achievements) == 1
        assert achievements[0][1] == "Пробежал 5 км"
        assert achievements[0][2] == 0  # position

    def test_multiple_achievements(self, core_module, test_user):
        core_module.add_achievement(test_user, "Первый")
        core_module.add_achievement(test_user, "Второй")
        core_module.add_achievement(test_user, "Третий")

        items = core_module.get_user_achievements(test_user)
        assert len(items) == 3
        assert [it[2] for it in items] == [0, 1, 2]

    def test_get_achievements_all(self, core_module, test_user):
        core_module.add_achievement(test_user, "Достижение")
        all_items = core_module.get_achievements_all(test_user)
        assert len(all_items) == 1
        assert all_items[0][0] == 1  # position_1based
        assert all_items[0][1] == "Достижение"

    def test_get_achievements_by_period(self, core_module, test_user):
        core_module.add_achievement(test_user, "В рамках периода")
        today = date.today()
        records = core_module.get_achievements_by_period(
            test_user, today - timedelta(days=1), today + timedelta(days=1)
        )
        assert len(records) == 1

        records = core_module.get_achievements_by_period(
            test_user, date(2020, 1, 1), date(2020, 1, 31)
        )
        assert len(records) == 0

    def test_delete_achievement(self, core_module, test_user):
        core_module.add_achievement(test_user, "Будет удалено")
        core_module.add_achievement(test_user, "Останется")

        items = core_module.get_user_achievements(test_user)
        core_module.delete_achievement(items[0][0], test_user)

        remaining = core_module.get_user_achievements(test_user)
        assert len(remaining) == 1
        assert remaining[0][1] == "Останется"

    def test_update_achievement(self, core_module, test_user):
        core_module.add_achievement(test_user, "Старое название")
        items = core_module.get_user_achievements(test_user)
        core_module.update_achievement(items[0][0], "Новое название")

        updated = core_module.get_user_achievements(test_user)
        assert updated[0][1] == "Новое название"

    def test_count_achievements(self, core_module, test_user):
        assert core_module.count_achievements(test_user) == 0
        core_module.add_achievement(test_user, "1")
        core_module.add_achievement(test_user, "2")
        assert core_module.count_achievements(test_user) == 2

    def test_clean_achievement_text(self, core_module):
        assert core_module.clean_achievement_text("1. Пробежка") == "Пробежка"
        assert core_module.clean_achievement_text("2) Пробежка") == "Пробежка"
        assert core_module.clean_achievement_text("3 Пробежка") == "Пробежка"
        assert core_module.clean_achievement_text("1.2 Тест") == "Тест"
        assert core_module.clean_achievement_text("Уже чисто") == "Уже чисто"
        assert core_module.clean_achievement_text("   С пробелами  ") == "С пробелами"


class TestExportExcel:
    """Экспорт в Excel."""

    def test_export_to_excel_empty(self, core_module):
        """Пустой экспорт не падает."""
        data = core_module.export_to_excel([])
        assert data.read(2) == b"PK"  # zip-сигнатура xlsx

    def test_export_to_excel(self, core_module, test_user):
        core_module.save_record(test_user, {
            "situation": "Тест",
            "thought": "Мысль",
        })
        records = core_module.get_records(test_user, days=30)
        data = core_module.export_to_excel(records)
        assert data.read(2) == b"PK"

    def test_export_achievements_to_excel(self, core_module, test_user):
        core_module.add_achievement(test_user, "Достижение 1")
        records = core_module.get_achievements_all(test_user)
        data = core_module.export_achievements_to_excel(records)
        assert data.read(2) == b"PK"

    def test_export_plans_to_excel(self, core_module, test_user):
        plan_id = core_module.get_or_create_plan(test_user, "2026-06-17")
        core_module.add_plan_item(plan_id, "Пункт 1")
        plans = core_module.get_plans_by_period(
            test_user, date(2026, 6, 1), date(2026, 6, 30)
        )
        data = core_module.export_plans_to_excel(plans, "test")
        assert data.read(2) == b"PK"


class TestFormatRecord:
    """Форматирование записи."""

    def test_format_record_none(self, core_module):
        result = core_module.format_record(None)
        assert "Запись не найдена" in result

    def test_format_record_with_data(self, core_module, test_user):
        core_module.save_record(test_user, {
            "situation": "Ситуация X",
            "thought": "Мысль Y",
            "emotion": "Тревога",
        })
        record = core_module.get_record_by_id(1, test_user)
        result = core_module.format_record(record)
        assert "#1" in result
        assert "Ситуация X" in result
        assert "Мысль Y" in result
        assert "Тревога" in result


class TestFreeLimits:
    """Проверка бесплатных лимитов (константы)."""

    def test_max_free_are_positive(self, core_module):
        assert core_module.MAX_FREE_RECORDS > 0
        assert core_module.MAX_FREE_PLANS > 0
        assert core_module.MAX_FREE_ACHIEVEMENTS > 0

    def test_users_count_separate(self, core_module, test_user):
        """Разные пользователи считаются отдельно."""
        user_x = 100
        user_y = 200

        for i in range(5):
            core_module.save_record(user_x, {"situation": f"X-{i}"})
            core_module.save_record(user_y, {"situation": f"Y-{i}"})

        assert core_module.get_records_count(user_x) == 5
        assert core_module.get_records_count(user_y) == 5

    def test_plans_separate_users(self, core_module, test_user):
        user_a = 100
        user_b = 200

        core_module.get_or_create_plan(user_a, "2026-06-17")
        core_module.get_or_create_plan(user_b, "2026-06-17")
        core_module.get_or_create_plan(user_b, "2026-06-18")

        assert core_module.count_user_plans(user_a) == 1
        assert core_module.count_user_plans(user_b) == 2
