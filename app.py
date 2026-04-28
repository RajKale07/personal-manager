from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "personal_manager_secret"


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


# Document issue guide data — procedure + required docs for each document type
ISSUE_GUIDE = {
    "Passport": {
        "procedure": [
            "Fill Form-1 online at passportindia.gov.in",
            "Book appointment at nearest Passport Seva Kendra",
            "Visit PSK with original documents on appointment date",
            "Biometric data and photo will be captured",
            "Police verification will be conducted",
            "Passport delivered to your address within 7-14 days",
        ],
        "required": ["Aadhaar Card", "Birth Certificate", "10th Marksheet", "Address Proof"],
    },
    "Driving License": {
        "procedure": [
            "Apply for Learner's License at sarathi.parivahan.gov.in",
            "Pass the online theory test",
            "Wait 30 days after Learner's License",
            "Book driving test slot at RTO",
            "Appear for practical driving test at RTO",
            "License issued if test passed",
        ],
        "required": ["Aadhaar Card", "Address Proof", "Age Proof", "Passport Photo"],
    },
    "Aadhaar Card": {
        "procedure": [
            "Visit nearest Aadhaar Enrollment Centre",
            "Fill enrollment form",
            "Submit biometric data (fingerprints + iris scan)",
            "Get acknowledgement slip with enrollment ID",
            "Download e-Aadhaar from uidai.gov.in after 90 days",
        ],
        "required": ["Birth Certificate", "Address Proof", "Passport Photo"],
    },
    "PAN Card": {
        "procedure": [
            "Apply online at tin-nsdl.com or utiitsl.com",
            "Fill Form 49A with personal details",
            "Upload photo, signature and supporting documents",
            "Pay application fee online",
            "PAN card delivered within 15 working days",
        ],
        "required": ["Aadhaar Card", "Birth Certificate", "Address Proof", "Passport Photo"],
    },
    "Voter ID": {
        "procedure": [
            "Apply online at voters.eci.gov.in",
            "Fill Form 6 for new registration",
            "Upload required documents",
            "BLO will verify your details at your address",
            "Voter ID card issued after verification",
        ],
        "required": ["Aadhaar Card", "Address Proof", "Passport Photo", "Age Proof"],
    },
    "Vehicle RC": {
        "procedure": [
            "Visit RTO with vehicle and documents",
            "Fill Form 20 for registration",
            "Vehicle inspection by RTO officer",
            "Pay registration fee",
            "RC issued within 7 working days",
        ],
        "required": ["Driving License", "Insurance Policy", "Address Proof", "PAN Card"],
    },
    "Insurance Policy": {
        "procedure": [
            "Compare plans on insurance aggregator websites",
            "Choose plan based on coverage and premium",
            "Fill proposal form with personal and health details",
            "Pay premium online",
            "Policy document sent to registered email",
        ],
        "required": ["Aadhaar Card", "PAN Card", "Address Proof", "Passport Photo"],
    },
    "Birth Certificate": {
        "procedure": [
            "Apply at Municipal Corporation / Gram Panchayat office",
            "Fill birth registration form",
            "Submit hospital discharge summary",
            "Certificate issued within 7 days of application",
        ],
        "required": ["Hospital Discharge Summary", "Parents Aadhaar Card", "Address Proof"],
    },
}


def normalize_text(value):
    return value.strip().lower() if value else ""


def find_guide(document_query):
    query = normalize_text(document_query)
    if not query:
        return None, None

    for doc_name, info in ISSUE_GUIDE.items():
        if normalize_text(doc_name) == query:
            return doc_name, info

    for doc_name, info in ISSUE_GUIDE.items():
        if query in normalize_text(doc_name):
            return doc_name, info

    return None, None


def build_issue_advisor(document_query, user_doc_names):
    selected_name, info = find_guide(document_query)
    if not selected_name:
        return None, None

    owned_set = set(user_doc_names)
    required = info["required"]
    owned_required = [req for req in required if normalize_text(req) in owned_set]
    missing_required = [req for req in required if normalize_text(req) not in owned_set]
    readiness_total = len(required)
    readiness_pct = int((len(owned_required) / readiness_total) * 100) if readiness_total else 0

    return {
        "name": selected_name,
        "procedure": info["procedure"],
        "required": required,
        "owned_required": owned_required,
        "missing_required": missing_required,
        "readiness_pct": readiness_pct,
        "document_owned": normalize_text(selected_name) in owned_set,
    }, selected_name


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
            session["is_admin"] = email == "admin@example.com"
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

    cursor.close()
    conn.close()

    user_doc_names = [normalize_text(doc[2]) for doc in documents]
    selected_document_query = request.args.get("document", "").strip()
    selected_guide, selected_document_name = build_issue_advisor(selected_document_query, user_doc_names)
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
        guide_names=sorted(ISSUE_GUIDE.keys()),
        selected_document_query=selected_document_query,
        selected_guide=selected_guide,
        selected_document_name=selected_document_name,
        advisor_message=advisor_message,
    )


@app.route("/add_document", methods=["POST"])
def add_document():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO documents (user_id, document_name, authority, issue_date, expiry_date, importance) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                session["user_id"],
                request.form["document_name"],
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

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, created_date FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT d.*, u.name FROM documents d JOIN users u ON d.user_id = u.user_id")
    documents = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", users=users, documents=documents)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/favicon.ico")
def favicon():
    return make_response("", 204)


if __name__ == "__main__":
    app.run(debug=True)
