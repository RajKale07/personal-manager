# Project Structure — Personal Manager

## Directory Layout
```
DBMS/
├── app.py                  # Flask backend — all routes, DB logic, ISSUE_GUIDE data
├── setup_database.sql      # Primary SQL schema: tables, view, stored procedure, sample data
├── add_tasks_table.sql     # Migration: adds tasks table (document_id FK, task_type, status)
├── database_setup.sql      # Older/duplicate SQL schema (not primary)
├── personal_manager.py     # Legacy CLI version (unused in web app)
├── README.md               # Setup and usage documentation
└── templates/
    ├── login.html          # Login form
    ├── register.html       # Registration form
    ├── dashboard.html      # User dashboard: documents, expiry alerts, tasks, issue guide
    └── admin.html          # Admin panel: all users and documents
```

## Database Tables
| Table       | Key Columns                                                        |
|-------------|--------------------------------------------------------------------|
| users       | user_id, name, email, password, created_date                       |
| documents   | document_id, user_id, document_name, authority, issue_date, expiry_date, importance |
| tasks       | task_id, user_id, document_id (FK), task_type, status              |
| deadlines   | deadline_id, user_id, title, description, due_date, status         |
| goals       | goal_id, user_id, goal_name, start_date, target_date, progress, status |
| contacts    | contact_id, user_id, contact_name, relationship, phone             |

- View: `expiring_documents` — documents expiring within 30 days
- Stored Procedure: `get_upcoming_deadlines()` — deadlines due within 7 days

## Core Components

### app.py
Single-file Flask application. Contains:
- `get_db()` — creates and returns a MySQL connection
- `ISSUE_GUIDE` — dict mapping document names to procedure steps and required documents
- All route handlers: login, register, dashboard, add_document, mark_task_done, admin, logout

### Route → Template Mapping
| Route              | Template         |
|--------------------|------------------|
| `/`                | login.html       |
| `/register`        | register.html    |
| `/dashboard`       | dashboard.html   |
| `/admin`           | admin.html       |

## Architectural Pattern
- Monolithic single-file Flask app (no blueprints)
- No ORM — raw SQL via mysql-connector-python cursor
- Server-side rendered HTML templates (Jinja2)
- Session-based auth (Flask session, secret key)
- Admin identity determined by hardcoded email check (`admin@example.com`)
