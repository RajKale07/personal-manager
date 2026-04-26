from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "personal_manager_secret"

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1", port=3306, user="root",
        password="Raj@2904", database="personal_manager",
        charset='utf8mb4', use_pure=True
    )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close(); conn.close()
        if user and user[2] == password:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["is_admin"] = (email == "admin@example.com")
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
            from datetime import date
            cursor.execute(
                "INSERT INTO users (name, email, password, created_date) VALUES (%s, %s, %s, %s)",
                (name, email, password, date.today())
            )
            conn.commit()
            flash("Registered successfully! Please login.")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error: {e}")
        finally:
            cursor.close(); conn.close()
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE user_id = %s", (session["user_id"],))
    documents = cursor.fetchall()
    cursor.execute(
        "SELECT document_name, expiry_date, DATEDIFF(expiry_date, CURDATE()) as days_left FROM documents "
        "WHERE user_id = %s AND expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) ORDER BY expiry_date",
        (session["user_id"],)
    )
    expiring = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("dashboard.html", documents=documents, expiring=expiring)

@app.route("/add_document", methods=["POST"])
def add_document():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO documents (user_id, document_name, authority, issue_date, expiry_date, importance) VALUES (%s,%s,%s,%s,%s,%s)",
            (session["user_id"], request.form["document_name"], request.form["authority"],
             request.form["issue_date"], request.form["expiry_date"], request.form["importance"])
        )
        conn.commit()
        flash("Document added successfully!")
    except Exception as e:
        flash(f"Error: {e}")
    finally:
        cursor.close(); conn.close()
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
    cursor.close(); conn.close()
    return render_template("admin.html", users=users, documents=documents)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
