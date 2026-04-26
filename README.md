# Personal Manager

A web-based personal document manager built with **Flask** and **MySQL**. Users can register, log in, add their important documents, and get notified when documents are about to expire. Admins can view all users and their documents.

---

## Project Structure

```
DBMS/
├── app.py                  # Flask backend — all routes and logic
├── setup_database.sql      # MySQL schema + sample data (run this first)
├── personal_manager.py     # Old CLI version (no longer used)
├── database_setup.sql      # Duplicate SQL file (older version)
└── templates/
    ├── login.html          # Login page
    ├── register.html       # Register page
    ├── dashboard.html      # User dashboard
    └── admin.html          # Admin panel
```

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python 3, Flask         |
| Database  | MySQL 8.0               |
| Frontend  | HTML, CSS (no framework)|
| Connector | mysql-connector-python  |

---

## Database Schema

### Tables

- **users** — stores registered users (user_id, name, email, password, created_date)
- **documents** — stores user documents (document_id, user_id, document_name, authority, issue_date, expiry_date, importance)
- **deadlines** — stores deadlines (deadline_id, user_id, title, description, due_date, status)
- **goals** — stores goals (goal_id, user_id, goal_name, start_date, target_date, progress, status)
- **contacts** — stores contacts (contact_id, user_id, contact_name, relationship, phone)

### View

- **expiring_documents** — returns all documents expiring within the next 30 days

### Stored Procedure

- **get_upcoming_deadlines()** — returns deadlines due within the next 7 days

---

## How It Works

### 1. User Registration & Login
- User registers at `/register` with name, email, and password
- On login at `/`, email and password are matched against the `users` table
- If email is `admin@example.com`, user is redirected to the **Admin Panel**
- Otherwise, user is redirected to the **Dashboard**
- Session stores `user_id`, `name`, and `is_admin` flag

### 2. User Dashboard (`/dashboard`)
- Shows a form to **add a new document** (name, authority, issue date, expiry date, importance)
- Shows a table of **all documents** belonging to the logged-in user
- Shows a **notification banner** if any document is expiring within the next 30 days, with days remaining

### 3. Document Expiry Notifications
- On every dashboard load, the app queries documents expiring within 30 days for that user
- A highlighted alert banner is shown at the top listing each expiring document and how many days are left
- Color coded: urgent if ≤ 7 days, warning if ≤ 30 days

### 4. Admin Panel (`/admin`)
- Only accessible if logged in as `admin@example.com`
- Shows a table of **all registered users**
- Shows a table of **all documents** across all users with the owner's name

---

## Setup Instructions

### Prerequisites
- Python 3.x
- MySQL 8.0
- pip

### Step 1 — Install dependencies
```
pip install flask mysql-connector-python
```

### Step 2 — Set up the database
Open cmd and run:
```
mysql -u root -p < "path\to\setup_database.sql"
```
This creates the `personal_manager` database, all tables, the view, stored procedure, and inserts sample data.

### Step 3 — Configure password
In `app.py`, update the password in `get_db()`:
```python
password="your_mysql_root_password"
```

### Step 4 — Run the app
```
python app.py
```
Open your browser at `http://127.0.0.1:5000`

---

## Sample Login Credentials

| Role  | Email                  | Password     |
|-------|------------------------|--------------|
| User  | john@example.com       | password123  |
| User  | jane@example.com       | password456  |
| Admin | admin@example.com      | admin123     |

> To create the admin account, run this in MySQL:
> ```sql
> INSERT INTO users (name, email, password, created_date)
> VALUES ('Admin', 'admin@example.com', 'admin123', CURDATE());
> ```

---

## Pages & Routes

| Route          | Method    | Description                        |
|----------------|-----------|------------------------------------|
| `/`            | GET, POST | Login page                         |
| `/register`    | GET, POST | Register new user                  |
| `/dashboard`   | GET       | User dashboard with documents      |
| `/add_document`| POST      | Add a new document                 |
| `/admin`       | GET       | Admin panel (admin only)           |
| `/logout`      | GET       | Clear session and redirect to login|

---

## Features

- User authentication (login / register)
- Add and view personal documents
- Document expiry notifications (30-day warning on dashboard)
- Admin panel to monitor all users and documents
- Dark professional UI theme
- Importance badges (High / Medium / Low) with color coding

---

## Known Limitations

- Passwords are stored as plain text (no hashing) — for demo/college use only
- No email notifications — reminders are shown on the dashboard only
- Goals and deadlines tables exist in the DB but are not used in the web app yet
