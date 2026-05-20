LTO Console App

Minimal console application that connects to the `lto` MariaDB database and calls stored procedures.

Setup

1. Create and import your `SQL_Statements.sql` into a MariaDB `lto` database.
2. Create a Python virtualenv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Edit `main.py` to set correct DB credentials.

Run

```bash
python main.py
```

Notes

- The UI maps to stored procedures by name; ensure your `SQL_Statements.sql` exposes the procedures listed in `UI_Heirarchy.txt`.
- Renew operations intentionally do not prompt for OR info; stored procedures should handle copying previous OR values.
