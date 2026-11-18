
# Habit Tracking Application

## Project Overview

A command-line Habit Tracking Application developed in Python for the **Object-Oriented and Functional Programming with Python** module at IU International University of Applied Sciences.

The application allows users to create, manage, and analyse daily and weekly habits using object-oriented programming, functional programming techniques, and SQLite database persistence.

## Features

- Create and manage daily or weekly habits.
- Record habit completions.
- View all habits or filter by periodicity.
- Calculate longest daily and weekly completion streaks.
- Store habit creation dates.
- Save and retrieve data using SQLite.
- Delete habits and their completion histories.
- Optionally load five predefined habits with four weeks of simulated completion data.

## Technologies

- Python 3
- SQLite
- pytest
- Visual Studio

## Project Structure

```text
habit_tracking_app/
├── habit_tracking_app.py
├── test_habit_tracking.py
├── README.md
└── habits.db
```

The SQLite database is generated locally when the application runs.

## Installation and Usage

Ensure Python 3 is installed.

Run the application:

```bash
python habit_tracking_app.py
```

Follow the interactive menu to create, view, complete, analyse, or delete habits.

When prompted, choose whether to load the sample dataset.

## Sample Dataset

The application provides five predefined demonstration habits:

| Habit | Periodicity |
|---|---|
| Reading a Book | Daily |
| Reading the Bible | Daily |
| Going to the Gym | Daily |
| Grocery Shopping | Weekly |
| Checking Investment Performance | Weekly |

The dataset contains four weeks of simulated completion records, including missed days. Sample data is inserted only when no habits already exist in the database.

## Application Design

The application uses two main classes:

- **Habit:** Stores habit details, creation date, and completion history.
- **HabitTracker:** Manages the collection of habits.

Separate functions handle database operations, filtering, and streak calculations.

Daily streaks use consecutive calendar days, while weekly streaks use consecutive calendar weeks.

## Testing

Automated testing is performed using pytest.

Install pytest if necessary:

```bash
python -m pip install pytest
```

Run the tests:

```bash
python -m pytest -v
```

**Latest result: 15 tests passed.**

Tests cover habit creation, completion tracking, streak calculations, database persistence, deletion, filtering, and creation-date persistence.

## Portfolio Phases

### Phase 1 — Conception

Defined the project objectives, requirements, programming approach, application structure, and SQLite database design.

**Status:** Completed and approved.

### Phase 2 — Implementation and Presentation

Implemented the Python application, SQLite persistence, habit analysis, and automated testing.

The accompanying presentation will explain the methodology, architecture, implementation, testing, and reflection.

**Status:** Coding and testing completed; presentation pending.

### Phase 3 — Final Submission

Final preparation includes the project repository, supporting documentation, presentation, and a short abstract containing the repository link.

**Status:** Pending.

## Limitations

- Command-line interface only.
- Local SQLite storage.
- Demonstration data is simulated.
- Habits created before creation-date support may not retain their original creation timestamps.

## Conclusion

The project demonstrates practical object-oriented and functional programming through a working Python habit tracker with persistent storage, habit analysis, and automated testing.
