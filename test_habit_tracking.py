
import sqlite3
import pytest

from datetime import datetime



from habit_tracking_app import (
    Habit,
    HabitTracker,
    calculate_longest_streak,
    calculate_weekly_streak,
    initialize_database,
    save_habit_to_database,
    load_habits_from_database,
    save_completion_to_database,
    delete_habit_from_database,
    get_unique_completion_dates,
    filter_habits_by_periodicity
)


def test_create_habit():
    habit = Habit("Reading", "daily")
    assert habit.name == "Reading"
    assert habit.periodicity == "daily"


def test_add_habit():
    tracker = HabitTracker()
    tracker.add_habit(Habit("Exercise", "weekly"))
    assert len(tracker.habits) == 1


def test_complete_habit():
    habit = Habit("Reading", "daily")
    habit.complete()
    assert len(habit.completions) == 1


def test_daily_streak():
    dates = [
        datetime(2026, 11, 1).date(),
        datetime(2026, 11, 2).date(),
        datetime(2026, 11, 3).date(),
    ]
    assert calculate_longest_streak(dates) == 3


def test_weekly_streak():
    completions = [
        datetime(2026, 11, 2),
        datetime(2026, 11, 9),
        datetime(2026, 11, 16),
    ]
    assert calculate_weekly_streak(completions) == 3


def test_duplicate_weekly_completions():
    completions = [
        datetime(2026, 11, 2),
        datetime(2026, 11, 4),
        datetime(2026, 11, 9),
    ]
    assert calculate_weekly_streak(completions) == 2


def test_empty_streak():
    assert calculate_longest_streak([]) == 0
    assert calculate_weekly_streak([]) == 0



@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    database_path = tmp_path / "habits.db"

    original_connect = sqlite3.connect

    def connect_to_test_database(database):
        return original_connect(str(database_path))

    monkeypatch.setattr(
        "habit_tracking_app.sqlite3.connect",
        connect_to_test_database
    )

    initialize_database()
    return database_path


def test_save_habit_to_database(temporary_database):
    habit = Habit("Swimming", "weekly")

    save_habit_to_database(habit)

    assert habit.id is not None


def test_load_habit_from_database(temporary_database):
    habit = Habit("Reading", "daily")
    save_habit_to_database(habit)

    tracker = HabitTracker()
    load_habits_from_database(tracker)

    assert len(tracker.habits) == 1
    assert tracker.habits[0].name == "Reading"


def test_delete_habit_from_database(temporary_database):
    from habit_tracking_app import delete_habit_from_database

    habit = Habit("Walking", "daily")
    save_habit_to_database(habit)

    delete_habit_from_database(habit)

    tracker = HabitTracker()
    load_habits_from_database(tracker)

    assert len(tracker.habits) == 0


def test_completion_persistence(temporary_database):
    habit = Habit("Swimming", "weekly")
    save_habit_to_database(habit)

    save_completion_to_database(habit)

    tracker = HabitTracker()
    load_habits_from_database(tracker)

    loaded_habit = tracker.habits[0]

    assert len(loaded_habit.completions) == 1
    assert calculate_weekly_streak(loaded_habit.completions) == 1


def test_deletion_removes_completion_history(temporary_database):
    habit = Habit("Walking", "daily")
    save_habit_to_database(habit)
    save_completion_to_database(habit)

    habit_id = habit.id
    delete_habit_from_database(habit)

    connection = sqlite3.connect("habits.db")
    remaining = connection.execute(
        "SELECT COUNT(*) FROM completions WHERE habit_id = ?",
        (habit_id,)
    ).fetchone()[0]
    connection.close()

    assert remaining == 0


def test_unique_completion_dates():
    completions = [
        datetime(2026, 11, 2, 9, 0),
        datetime(2026, 11, 2, 18, 0),
        datetime(2026, 11, 3, 10, 0),
    ]

    result = get_unique_completion_dates(completions)

    assert result == [
        datetime(2026, 11, 2).date(),
        datetime(2026, 11, 3).date(),
    ]

    assert len(completions) == 3

def test_filter_habits_by_periodicity():
    habits = [
        Habit("Reading", "daily"),
        Habit("Exercise", "daily"),
        Habit("Shopping", "weekly")
    ]

    daily_habits = filter_habits_by_periodicity(habits, "daily")
    weekly_habits = filter_habits_by_periodicity(habits, "weekly")

    assert len(daily_habits) == 2
    assert len(weekly_habits) == 1

    assert daily_habits[0].name == "Reading"
    assert daily_habits[1].name == "Exercise"
    assert weekly_habits[0].name == "Shopping"

    # Filtering must not modify the original collection.
    assert len(habits) == 3

def test_creation_date_persistence(temporary_database):
    habit = Habit("Reading", "daily")
    original_creation_date = habit.created_at

    save_habit_to_database(habit)

    tracker = HabitTracker()
    load_habits_from_database(tracker)

    assert len(tracker.habits) == 1
    assert tracker.habits[0].created_at == original_creation_date

