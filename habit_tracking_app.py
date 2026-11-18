
from datetime import datetime, timedelta
import sqlite3


# =========================
# HABIT CLASS
# =========================

class Habit:
    """Represent a daily or weekly habit and its completion history."""
    def __init__(self, name, periodicity):
        self.id = None
        self.name = name
        self.periodicity = periodicity
        self.created_at = datetime.now()
        self.completions = []

    def complete(self):
        """Record a completion using the current date and time."""
        completion_time = datetime.now()
        self.completions.append(completion_time)

    def get_longest_streak(self):
        """Return the longest streak of consecutive completed days."""
        completion_dates = [
            completion.date() for completion in self.completions
        ]

        sorted_dates = sorted(set(completion_dates))
        return calculate_longest_streak(sorted_dates)


# =========================
# HABIT TRACKER CLASS
# =========================

class HabitTracker:
    """Manage the collection of habits during an application session."""
    def __init__(self):
        self.habits = []

    def add_habit(self, habit):
        self.habits.append(habit)

def filter_habits_by_periodicity(habits, periodicity):
    """Return habits matching the requested periodicity."""
    return [
        habit
        for habit in habits
        if habit.periodicity == periodicity
    ]


# =========================
# STREAK ANALYSIS
# =========================

def get_unique_completion_dates(completions):
    """Return sorted, unique completion dates without modifying the input."""
    return sorted({completion.date() for completion in completions})


def calculate_longest_streak(completion_dates):
    """Calculate the longest streak of consecutive days."""
    if not completion_dates:
        return 0

    current_streak = 1
    longest_streak = 1

    for i in range(1, len(completion_dates)):
        difference = completion_dates[i] - completion_dates[i - 1]

        if difference.days == 1:
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

    return longest_streak


def calculate_weekly_streak(completions):
    """Calculate the longest streak of consecutive calendar weeks."""
    if not completions:
        return 0

    week_starts = []

    for completion in completions:
        date = completion.date()
        monday = date.toordinal() - date.weekday()
        week_starts.append(monday)

    unique_weeks = sorted(set(week_starts))

    current_streak = 1
    longest_streak = 1

    for i in range(1, len(unique_weeks)):
        difference = unique_weeks[i] - unique_weeks[i - 1]

        if difference == 7:
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

    return longest_streak

# =========================
# DATABASE FUNCTIONS
# =========================

def initialize_database():
    """Create the SQLite tables if they do not exist."""
    connection = sqlite3.connect("habits.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            periodicity TEXT NOT NULL
        )
    """)
    # Add creation dates to databases created before this feature.
    cursor.execute("PRAGMA table_info(habits)")
    columns = [column[1] for column in cursor.fetchall()]

    if "created_at" not in columns:
        cursor.execute(
            "ALTER TABLE habits ADD COLUMN created_at TEXT"
        )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_time TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        )
    """)

    connection.commit()
    connection.close()


def save_habit_to_database(habit):
    """Save a habit and assign its database ID."""
    connection = sqlite3.connect("habits.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO habits (name, periodicity, created_at)
        VALUES (?, ?, ?)
        """,
        (
            habit.name,
            habit.periodicity,
            habit.created_at.isoformat()
        )
)
    connection.commit()
    habit.id = cursor.lastrowid
    connection.close()


def save_completion_to_database(habit):
    """Save a completion timestamp and update the habit history."""
    if habit.id is None:
        raise ValueError("Habit must be saved before recording completions.")

    completion_time = datetime.now()

    connection = sqlite3.connect("habits.db")

    try:
        connection.execute(
            """
            INSERT INTO completions (habit_id, completion_time)
            VALUES (?, ?)
            """,
            (habit.id, completion_time.isoformat())
        )
        connection.commit()
    finally:
        connection.close()

    habit.completions.append(completion_time)



def load_habits_from_database(tracker):
    """Load saved habits and completion histories into the tracker."""
    connection = sqlite3.connect("habits.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, periodicity, created_at FROM habits"
    )
    saved_habits = cursor.fetchall()
    for habit_id, name, periodicity, created_at in saved_habits:
        habit = Habit(name, periodicity)
        habit.id = habit_id

        if created_at is not None:
            habit.created_at = datetime.fromisoformat(created_at)

        cursor.execute(
            """
            SELECT completion_time
            FROM completions
            WHERE habit_id = ?
            ORDER BY completion_time
            """,
            (habit_id,)
        )

        saved_completions = cursor.fetchall()

        for (completion_time,) in saved_completions:
            habit.completions.append(
                datetime.fromisoformat(completion_time)
            )

        tracker.add_habit(habit)

    connection.close()

def delete_habit_from_database(habit):
    """Delete a habit and its completion history from SQLite."""
    connection = sqlite3.connect("habits.db")

    try:
        connection.execute(
            "DELETE FROM completions WHERE habit_id = ?",
            (habit.id,)
        )

        connection.execute(
            "DELETE FROM habits WHERE id = ?",
            (habit.id,)
        )

        connection.commit()
    finally:
        connection.close()
def seed_sample_habits():
    """Add five demonstration habits to an empty database."""

    connection = sqlite3.connect("habits.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM habits")
    habit_count = cursor.fetchone()[0]
    connection.close()

    # Do not add sample data to an existing habit collection.
    if habit_count > 0:
        return

    sample_habits = [
        ("Reading a Book", "daily"),
        ("Reading the Bible", "daily"),
        ("Going to the Gym", "daily"),
        ("Grocery Shopping", "weekly"),
        ("Checking Investment Performance", "weekly"),
    ]

    today = datetime.now().date()

    for habit_index, (name, periodicity) in enumerate(sample_habits):
        habit = Habit(name, periodicity)
        save_habit_to_database(habit)

        if periodicity == "daily":
            # Demonstrate a mixture of completed and missed days.
            offsets = [
                days_ago
                for days_ago in range(27, -1, -1)
                if (days_ago + habit_index) % 6 != 0
            ]
        else:
            # One completion in each of four consecutive weeks.
            offsets = [24, 17, 10, 3]

        connection = sqlite3.connect("habits.db")

        try:
            for days_ago in offsets:
                completion_date = today - timedelta(days=days_ago)
                completion_time = datetime.combine(
                    completion_date,
                    datetime.min.time()
                ).replace(hour=18)

                connection.execute(
                    """
                    INSERT INTO completions (habit_id, completion_time)
                    VALUES (?, ?)
                    """,
                    (habit.id, completion_time.isoformat())
                )

            connection.commit()
        finally:
            connection.close()

# =========================
# MAIN APPLICATION
# =========================

def main():
    initialize_database()

    demo_choice = input(
        "Load five sample habits with four weeks of demonstration data? (yes/no): "
    ).strip().lower()

    if demo_choice == "yes":
        seed_sample_habits()

    tracker = HabitTracker()
    load_habits_from_database(tracker)

    print("Welcome to the Habit Tracking App!")

    while True:
        print("\n===== HABIT TRACKING APP =====")
        print("1. Create a habit")
        print("2. View all habits")
        print("3. Complete a habit")
        print("4. View habit streaks")
        print("5. Delete a habit")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            name = input("Enter habit name: ").strip()
            periodicity = input(
                "Enter periodicity (daily/weekly): "
            ).strip().lower()

            if not name:
                print("Habit name cannot be empty.")

            elif periodicity not in ["daily", "weekly"]:
                print("Invalid periodicity. Choose daily or weekly.")

            else:
                new_habit = Habit(name, periodicity)
                save_habit_to_database(new_habit)
                tracker.add_habit(new_habit)

                print("Habit created and saved successfully!")

        elif choice == "2":
            print("\nView habits:")
            print("1. All habits")
            print("2. Daily habits")
            print("3. Weekly habits")

            filter_choice = input("Choose an option (1-3): ").strip()

            if filter_choice == "1":
                selected_habits = tracker.habits
            elif filter_choice == "2":
                selected_habits = filter_habits_by_periodicity(
                    tracker.habits, "daily"
                )
            elif filter_choice == "3":
                selected_habits = filter_habits_by_periodicity(
                    tracker.habits, "weekly"
                )
            else:
                print("Invalid filter option.")
                continue

            if not selected_habits:
                print("No matching habits found.")
            else:
                print("\nYour habits:")

                for habit in selected_habits:
                    print(f"{habit.name} - {habit.periodicity}")

        elif choice == "3":
            if not tracker.habits:
                print("No habits available.")
            else:
                print("\nSelect a habit to complete:")

                for i, habit in enumerate(tracker.habits, start=1):
                    print(f"{i}. {habit.name}")

                selection = input("Enter habit number: ").strip()

                if selection.isdigit():
                    habit_number = int(selection)

                    if 1 <= habit_number <= len(tracker.habits):
                        selected_habit = tracker.habits[habit_number - 1]
                        save_completion_to_database(selected_habit)

                        print(
                            f"{selected_habit.name} completed successfully!"
                        )
                    else:
                        print("Invalid habit number.")
                else:
                    print("Please enter a valid number.")

        elif choice == "4":
            if not tracker.habits:
                print("No habits available.")
            else:
                print("\n===== HABIT PROGRESS =====")

                for habit in tracker.habits:
                    print(f"\nHabit: {habit.name}")
                    print(f"Periodicity: {habit.periodicity}")
                    print(f"Total completions: {len(habit.completions)}")

                    if habit.periodicity == "daily":
                        streak = habit.get_longest_streak()
                        unit = "day" if streak == 1 else "days"

                        print(f"Longest daily streak: {streak} {unit}")

                    else:
                        streak = calculate_weekly_streak(
                            habit.completions
                        )
                        unit = "week" if streak == 1 else "weeks"

                        print(f"Longest weekly streak: {streak} {unit}")


        elif choice == "5":
            if not tracker.habits:
                print("No habits available.")
            else:
                print("\nSelect a habit to delete:")

                for i, habit in enumerate(tracker.habits, start=1):
                    print(f"{i}. {habit.name}")

                selection = input("Enter habit number: ").strip()
                if selection.isdigit():
                    habit_number = int(selection)

                    if 1 <= habit_number <= len(tracker.habits):
                        selected_habit = tracker.habits[habit_number - 1]

                        confirmation = input(
                            f"Delete '{selected_habit.name}' and its history? (yes/no): "
                        ).strip().lower()

                        if confirmation == "yes":
                            delete_habit_from_database(selected_habit)
                            tracker.habits.remove(selected_habit)
                            print("Habit deleted successfully!")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Invalid habit number.")
                else:
                    print("Please enter a valid number.")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1-6.")

if __name__ == "__main__":
    main()
