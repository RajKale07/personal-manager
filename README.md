# Personal Manager

A web-based personal document management system built with **Flask** and **MySQL**. Users can register, log in, track their important documents, get notified before expiry, manage renewal tasks, and look up step-by-step issue procedures for Indian government documents.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [How It Works](#how-it-works)
- [Setup Instructions](#setup-instructions)
- [Sample Login Credentials](#sample-login-credentials)
- [Pages and Routes](#pages-and-routes)
- [Issue Guide — Supported Documents](#issue-guide--supported-documents)
- [Known Limitations](#known-limitations)

---

## Features

- User registration and login with session-based authentication
- Add and view personal documents (name, authority, issue date, expiry date, importance)
- Expiry notifications — urgent banner for documents expiring within 7 days, warning for within 30 days
- Expired document tracking with auto-created renewal tasks
- Task management — view pending renewal tasks and mark them as done
- Search-driven Issue Guide — type any document name to get the full issue procedure, required documents, what you already have, and what you still need (fully dynamic, stored in DB)
- Readiness progress bar showing how many required documents you already own
- Forgot password — reset password by verifying registered email
- Admin panel — view all registered users and all documents across the system
- Light cream UI theme with responsive layout

---

## Tech Stack

| Layer      | Technology               |
|------------|--------------------------|
| Backend    | Python 3.x, Flask        |
| Database   | MySQL 8.0                |
| Frontend   | HTML, CSS (no framework) |
| Templating | Jinja2                   |
| Connector  | mysql-connector-python   |

---

## Project Structure

```
DBMS/
├── app.py                   # Flask backend — all routes and DB logic
├── setup_database.sql       # Complete MySQL schema + sample data (run this first)
├── README.md                # This file
└── templates/
    ├── login.html           # Login page
    ├── register.html        # Register page
    ├── forgot_password.html # Reset password page
    ├── dashboard.html       # User dashboard — documents, tasks, issue guide
    └── admin.html           # Admin panel
```

---

## Database Schema

### Tables

| Table                  | Key Columns                                                                         |
|------------------------|-------------------------------------------------------------------------------------|
| `users`                | user_id, name, email, password, created_date                                        |
| `documents`            | document_id, user_id, document_name, authority, issue_date, expiry_date, importance |
| `tasks`                | task_id, user_id, document_id (FK), task_type, status                               |
| `issue_guide`          | guide_id, document_name                                                             |
| `issue_guide_steps`    | step_id, guide_id (FK), step_order, step_text                                       |
| `issue_guide_required` | req_id, guide_id (FK), required_document                                            |

### View

- **`expiring_documents`** — returns all documents with expiry date within the next 30 days

---

## How It Works

### 1. Registration and Login
- User registers at `/register` with name, email, and password
- On login at `/`, email and password are matched against the `users` table
- If the email is `admin@example.com`, the user is redirected to the Admin Panel
- Otherwise the user is redirected to the Dashboard
- Session stores `user_id`, `name`, and `is_admin`

### 2. Forgot Password
- User visits `/forgot-password` and enters their registered email
- System verifies the email exists in the DB
- If valid, the password is updated with the new one entered
- User is redirected to login with a success message

### 3. Dashboard
- Shows stats — total documents saved and pending renewal tasks
- Shows expiry notification banners at the top if any documents are expiring soon
- Sections: Add Document form, My Documents table, Renewal Tasks table
- Issue Guide search box — type a document name to get the full guide

### 4. Expiry Notifications
- Urgent banner (red) for documents expiring within 7 days
- Warning banner (amber) for documents expiring within 8–30 days
- Both banners list each document with the exact number of days remaining

### 5. Renewal Tasks
- When a document's expiry date passes, a `Renew` task is automatically created for it
- Duplicate tasks are prevented — the system checks before inserting
- Users can mark tasks as Done from the dashboard

### 6. Issue Guide
- User types a document name (e.g. Passport, PAN Card, Driving License) in the search box
- All guide data is loaded from the DB (`issue_guide`, `issue_guide_steps`, `issue_guide_required`)
- The dashboard shows:
  - Step-by-step procedure to obtain that document
  - Full list of required documents
  - Which required documents the user already has (green tags)
  - Which required documents are still missing (red tags)
  - A readiness progress bar showing the percentage of requirements met

### 7. Admin Panel
- Only accessible when logged in as `admin@example.com`
- Shows total user count and total document count
- Table of all registered users
- Table of all documents across all users with the owner's name

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
```
mysql -u root -p < "path\to\setup_database.sql"
```
This creates the `personal_manager` database, all tables, the view, and inserts sample data including the full issue guide.

### Step 3 — Create the admin account
Run this in MySQL after setup:
```sql
INSERT INTO users (name, email, password, created_date)
VALUES ('Admin', 'admin@example.com', 'admin123', CURDATE());
```

### Step 4 — Configure your DB password
In `app.py`, update the password inside `get_db()`:
```python
password="your_mysql_root_password"
```

### Step 5 — Run the app
```
python app.py
```
Open your browser at `http://127.0.0.1:5000`

---

## Sample Login Credentials

| Role  | Email              | Password     |
|-------|--------------------|--------------|\
| User  | john@example.com   | password123  |
| User  | jane@example.com   | password456  |
| Admin | admin@example.com  | admin123     |

---

## Pages and Routes

| Route                    | Method    | Description                              |
|--------------------------|-----------|------------------------------------------|
| `/`                      | GET, POST | Login page                               |
| `/register`              | GET, POST | Register a new user                      |
| `/forgot-password`       | GET, POST | Reset password by email verification     |
| `/dashboard`             | GET       | User dashboard                           |
| `/dashboard?document=X`  | GET       | Dashboard with issue guide result for X  |
| `/add_document`          | POST      | Add a new document                       |
| `/task/done/<task_id>`   | POST      | Mark a renewal task as done              |
| `/admin`                 | GET       | Admin panel (admin only)                 |
| `/logout`                | GET       | Clear session and redirect to login      |

---

## Issue Guide — Supported Documents

The issue guide data is stored in the database and can be updated directly via MySQL. Currently covers:

| Document          | Key Required Documents                                         |
|-------------------|----------------------------------------------------------------|
| Passport          | Aadhaar Card, Birth Certificate, 10th Marksheet, Address Proof |
| Driving License   | Aadhaar Card, Address Proof, Age Proof, Passport Photo         |
| Aadhaar Card      | Birth Certificate, Address Proof, Passport Photo               |
| PAN Card          | Aadhaar Card, Birth Certificate, Address Proof, Passport Photo |
| Voter ID          | Aadhaar Card, Address Proof, Passport Photo, Age Proof         |
| Vehicle RC        | Driving License, Insurance Policy, Address Proof, PAN Card     |
| Insurance Policy  | Aadhaar Card, PAN Card, Address Proof, Passport Photo          |
| Birth Certificate | Hospital Discharge Summary, Parents Aadhaar Card, Address Proof|

---

## Known Limitations

- Passwords are stored as plain text — for demo/college use only, not production
- No email notifications — expiry reminders are shown on the dashboard only
- No CSRF protection on POST routes
- `debug=True` is set in `app.run()` — must be disabled before any deployment
- Forgot password works by email verification only — no OTP or email link (college project)
