from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "personal_manager_secret"
ADMIN_EMAIL = "admin@example.com"


def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Raj@2904",
        database="personal_manager",
        charset="utf8mb4",
        use_pure=True,
    )


def normalize_text(value):
    return value.strip().lower() if value else ""


def load_issue_guide(cursor):
    """Load full issue guide from DB using 2 queries instead of N+1."""
    cursor.execute(
        "SELECT g.guide_id, g.document_name, s.step_text "
        "FROM issue_guide g "
        "JOIN issue_guide_steps s ON g.guide_id = s.guide_id "
        "ORDER BY g.document_name, s.step_order"
    )
    steps_rows = cursor.fetchall()

    cursor.execute(
        "SELECT g.guide_id, g.document_name, r.required_document "
        "FROM issue_guide g "
        "JOIN issue_guide_required r ON g.guide_id = r.guide_id "
        "ORDER BY g.document_name"
    )
    req_rows = cursor.fetchall()

    guide = {}
    for guide_id, doc_name, step_text in steps_rows:
        if doc_name not in guide:
            guide[doc_name] = {"procedure": [], "required": []}
        guide[doc_name]["procedure"].append(step_text)

    for guide_id, doc_name, req_doc in req_rows:
        if doc_name in guide:
            guide[doc_name]["required"].append(req_doc)

    return guide


def build_issue_advisor(document_query, user_doc_names, issue_guide):
    query = normalize_text(document_query)
    if not query:
        return None, None

    # Exact match first, then partial
    matched_name = None
    for doc_name in issue_guide:
        if normalize_text(doc_name) == query:
            matched_name = doc_name
            break
    if not matched_name:
        for doc_name in issue_guide:
            if query in normalize_text(doc_name):
                matched_name = doc_name
                break

    if not matched_name:
        return None, None

    info = issue_guide[matched_name]
    owned_set = set(user_doc_names)
    required = info["required"]
    owned_required = [r for r in required if normalize_text(r) in owned_set]
    missing_required = [r for r in required if normalize_text(r) not in owned_set]
    readiness_pct = int(len(owned_required) / len(required) * 100) if required else 0

    return {
        "name": matched_name,
        "procedure": info["procedure"],
        "required": required,
        "owned_required": owned_required,
        "missing_required": missing_required,
        "readiness_pct": readiness_pct,
        "document_owned": normalize_text(matched_name) in owned_set,
    }, matched_name


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[2] == password:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["is_admin"] = (email == ADMIN_EMAIL)
            return redirect(url_for("admin" if session["is_admin"] else "dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, created_date) VALUES (%s, %s, %s, %s)",
                (name, email, password, date.today()),
            )
            conn.commit()
            flash("Registered successfully! Please login.")
            return redirect(url_for("login"))
        except Exception as exc:
            flash(f"Error: {exc}")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM documents WHERE user_id = %s ORDER BY expiry_date",
        (session["user_id"],),
    )
    documents = cursor.fetchall()

    cursor.execute(
        "SELECT document_name, expiry_date, DATEDIFF(expiry_date, CURDATE()) as days_left FROM documents "
        "WHERE user_id = %s AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) "
        "ORDER BY expiry_date",
        (session["user_id"],),
    )
    expiring = cursor.fetchall()

    cursor.execute(
        "SELECT document_id, document_name, expiry_date FROM documents "
        "WHERE user_id = %s AND expiry_date < CURDATE() ORDER BY expiry_date DESC",
        (session["user_id"],),
    )
    expired = cursor.fetchall()

    for doc in expired:
        cursor.execute(
            "SELECT task_id FROM tasks WHERE user_id = %s AND document_id = %s AND task_type = 'Renew'",
            (session["user_id"], doc[0]),
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO tasks (user_id, document_id, task_type, status) VALUES (%s, %s, 'Renew', 'Pending')",
                (session["user_id"], doc[0]),
            )
    conn.commit()

    cursor.execute(
        "SELECT t.task_id, d.document_name, d.expiry_date, t.task_type, t.status "
        "FROM tasks t JOIN documents d ON t.document_id = d.document_id "
        "WHERE t.user_id = %s ORDER BY t.status ASC, d.expiry_date ASC",
        (session["user_id"],),
    )
    tasks = cursor.fetchall()

    issue_guide = load_issue_guide(cursor)
    cursor.close()
    conn.close()

    user_doc_names = [normalize_text(doc[2]) for doc in documents]
    selected_document_query = request.args.get("document", "").strip()
    selected_guide, selected_document_name = build_issue_advisor(selected_document_query, user_doc_names, issue_guide)
    advisor_message = None

    if selected_document_query and not selected_guide:
        advisor_message = (
            f'No issue guide found for "{selected_document_query}". '
            "Try one of the suggested document names."
        )

    notif_count = len(expiring) + len(expired)
    pending_tasks = sum(1 for task in tasks if task[4] == "Pending")

    return render_template(
        "dashboard.html",
        documents=documents,
        expiring=expiring,
        expired=expired,
        tasks=tasks,
        notif_count=notif_count,
        pending_tasks=pending_tasks,
        guide_names=sorted(issue_guide.keys()),
        selected_document_query=selected_document_query,
        selected_guide=selected_guide,
        selected_document_name=selected_document_name,
        advisor_message=advisor_message,
    )


@app.route("/add_document", methods=["POST"])
def add_document():
    if "user_id" not in session:
        return redirect(url_for("login"))

    doc_name = request.form["document_name"]
    if doc_name == "__other__":
        doc_name = request.form.get("custom_document_name", "").strip()
        if not doc_name:
            flash("Please enter a custom document name.")
            return redirect(url_for("dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO documents (user_id, document_name, authority, issue_date, expiry_date, importance) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                session["user_id"],
                doc_name,
                request.form["authority"],
                request.form["issue_date"],
                request.form["expiry_date"],
                request.form["importance"],
            ),
        )
        conn.commit()
        flash("Document added successfully!")
    except Exception as exc:
        flash(f"Error: {exc}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/document/delete/<int:doc_id>", methods=["POST"])
def delete_document(doc_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM documents WHERE document_id = %s AND user_id = %s",
        (doc_id, session["user_id"]),
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Document deleted.")
    return redirect(url_for("dashboard"))


@app.route("/document/edit/<int:doc_id>", methods=["POST"])
def edit_document(doc_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE documents SET document_name=%s, authority=%s, issue_date=%s, expiry_date=%s, importance=%s "
            "WHERE document_id=%s AND user_id=%s",
            (
                request.form["document_name"],
                request.form["authority"],
                request.form["issue_date"],
                request.form["expiry_date"],
                request.form["importance"],
                doc_id,
                session["user_id"],
            ),
        )
        conn.commit()
        flash("Document updated successfully!")
    except Exception as exc:
        flash(f"Error: {exc}")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("dashboard"))


@app.route("/task/done/<int:task_id>", methods=["POST"])
def mark_task_done(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'Done' WHERE task_id = %s AND user_id = %s",
        (task_id, session["user_id"]),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/admin")
def admin():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    view_user_id = request.args.get("user_id", "").strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, created_date FROM users ORDER BY user_id")
    users = cursor.fetchall()

    # Filter users by search
    filtered_users = []
    if search:
        sl = search.lower()
        filtered_users = [u for u in users if sl in u[1].lower() or sl in u[2].lower() or sl == str(u[0])]

    # Documents: only load when a specific user is selected
    selected_user = None
    documents = []
    if view_user_id and view_user_id.isdigit():
        cursor.execute("SELECT user_id, name, email FROM users WHERE user_id = %s", (int(view_user_id),))
        selected_user = cursor.fetchone()
        cursor.execute(
            "SELECT d.*, u.name FROM documents d JOIN users u ON d.user_id = u.user_id "
            "WHERE d.user_id = %s ORDER BY d.expiry_date",
            (int(view_user_id),),
        )
        documents = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "admin.html",
        users=users,
        filtered_users=filtered_users,
        documents=documents,
        search=search,
        view_user_id=view_user_id,
        selected_user=selected_user,
    )


@app.route("/admin/user/<int:uid>/edit", methods=["POST"])
def admin_edit_user(uid):
    if "user_id" not in session or not session.get("is_admin"):
        return redirect(url_for("login"))
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    new_password = request.form.get("new_password", "").strip()
    conn = get_db()
    cursor = conn.cursor()
    try:
        if new_password:
            cursor.execute(
                "UPDATE users SET name=%s, email=%s, password=%s WHERE user_id=%s",
                (name, email, new_password, uid),
            )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, email=%s WHERE user_id=%s",
                (name, email, uid),
            )
        conn.commit()
        flash(f"User #{uid} updated successfully.")
    except Exception as exc:
        flash(f"Error: {exc}")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("admin"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip()
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match.", "err")
            return render_template("forgot_password.html")

        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "err")
            return render_template("forgot_password.html")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            flash("No account found with that email address.", "err")
            return render_template("forgot_password.html")

        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Password reset successfully! You can now sign in.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
