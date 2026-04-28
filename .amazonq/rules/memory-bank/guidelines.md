# Development Guidelines — Personal Manager

## Code Quality Standards

### DB Connection Pattern
Always open and close connections per-request. Never reuse a connection across requests.
```python
conn = get_db()
cursor = conn.cursor()
try:
    cursor.execute("...", (params,))
    conn.commit()
except Exception as e:
    flash(f"Error: {e}")
finally:
    cursor.close(); conn.close()
```
- Use `finally` for cleanup in write operations (INSERT/UPDATE)
- For read-only routes, inline close is acceptable: `cursor.close(); conn.close()`

### Auth Guard Pattern
Every protected route must check session at the top before any DB call:
```python
if "user_id" not in session:
    return redirect(url_for("login"))
```
Admin routes additionally check:
```python
if "user_id" not in session or not session.get("is_admin"):
    return redirect(url_for("login"))
```

### SQL Style
- Always use parameterized queries with `%s` placeholders — never string interpolation
- Multi-line SQL strings use implicit string concatenation (no backslash continuation):
```python
cursor.execute(
    "SELECT t.task_id, d.document_name "
    "FROM tasks t JOIN documents d ON t.document_id = d.document_id "
    "WHERE t.user_id = %s",
    (session["user_id"],)
)
```
- Parameters always passed as a tuple, even for single values: `(value,)`

### Flash Messages
- Success: plain string — `flash("Document added successfully!")`
- Error: f-string with exception — `flash(f"Error: {e}")`

### Redirect After POST
Always redirect after a successful POST to prevent form resubmission:
```python
return redirect(url_for("dashboard") + "?tab=documents")
```
Tab state is passed as a query string parameter (`?tab=tasks`, `?tab=documents`).

## Naming Conventions
- Route functions: `snake_case` matching the URL path (e.g., `add_document`, `mark_task_done`)
- Template variables: `snake_case` (e.g., `user_doc_names`, `notif_count`, `expiring`)
- SQL table/column names: `snake_case`
- Constants/static data: `UPPER_SNAKE_CASE` (e.g., `ISSUE_GUIDE`)

## Structural Conventions
- All routes live in `app.py` — no blueprints, no separate modules
- Static data (like `ISSUE_GUIDE`) is defined as a module-level dict, not in the DB
- Session keys used: `user_id`, `name`, `is_admin`
- `is_admin` is set at login time by comparing email to `"admin@example.com"`
- `date.today()` used for inserting current date (not `datetime.now()`)

## Template Data Pattern
Pass all template variables as named kwargs to `render_template`:
```python
return render_template("dashboard.html",
    documents=documents,
    expiring=expiring,
    tasks=tasks,
    notif_count=notif_count,
    issue_guide=ISSUE_GUIDE,
    user_doc_names=user_doc_names
)
```

## Auto-Task Creation Pattern
When a business rule requires auto-generating records (e.g., renewal tasks for expired docs), check for existence before inserting to avoid duplicates:
```python
for doc in expired:
    cursor.execute(
        "SELECT task_id FROM tasks WHERE user_id = %s AND document_id = %s AND task_type = 'Renew'",
        (session["user_id"], doc[0])
    )
    if not cursor.fetchone():
        cursor.execute("INSERT INTO tasks ...", (...))
conn.commit()  # Single commit after the loop
```

## Known Limitations to Be Aware Of
- Passwords stored as plain text — do not add hashing without updating login comparison logic
- No CSRF protection on POST routes
- `debug=True` is set in `app.run()` — must be disabled for any non-local deployment
- `goals`, `deadlines`, `contacts` tables exist in DB but have no web routes yet — add routes in `app.py` following the existing pattern
