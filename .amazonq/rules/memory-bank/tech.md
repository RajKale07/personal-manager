# Tech Stack — Personal Manager

## Languages
- Python 3.x — backend logic and routing
- SQL (MySQL 8.0) — schema, queries, view, stored procedure
- HTML + CSS — frontend templates (no JS framework, no CSS framework)
- Jinja2 — server-side templating (via Flask)

## Dependencies
| Package                  | Purpose                          |
|--------------------------|----------------------------------|
| flask                    | Web framework, routing, sessions |
| mysql-connector-python   | MySQL database connector         |

Install:
```
pip install flask mysql-connector-python
```

## Database
- MySQL 8.0
- Database name: `personal_manager`
- Connection via `mysql.connector.connect()` in `get_db()`
- Default user: `root`, password must be set in `app.py`

## Development Commands

### Database setup (run once)
```
mysql -u root -p < "path\to\setup_database.sql"
```

### Apply tasks table migration
```
mysql -u root -p personal_manager < "path\to\add_tasks_table.sql"
```

### Run the app
```
python app.py
```
App runs at `http://127.0.0.1:5000` with `debug=True`

## Configuration
- `app.secret_key` — set in app.py (change for production)
- DB password — hardcoded in `get_db()`, update before running
- Admin account — must be manually inserted into `users` table with email `admin@example.com`
