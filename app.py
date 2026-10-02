from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from pathlib import Path
from functools import wraps

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "temporary-development-secret-change-me"
)

DB = Path("harkish_verse.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        try:
            with get_db() as conn:
                conn.execute(
                    """
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                    """,
                    (name, email, hashed_password)
                )
                conn.commit()

        except sqlite3.IntegrityError:
            flash(
                "An account with this email already exists.",
                "error"
            )
            return redirect(url_for("signup"))

        flash(
            "Account created successfully. Please log in.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("signup.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(
            user["password"],
            password
        ):
            session.clear()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            flash("Login successful.", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# LOGIN REQUIRED
def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():

    with get_db() as conn:

        user_count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        message_count = conn.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]

    return render_template(
        "dashboard.html",
        name=session.get("user_name"),
        email=session.get("user_email"),
        user_count=user_count,
        message_count=message_count
    )


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))


# CONTACT
@app.post("/contact")
def contact():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:

        flash(
            "Please fill in all fields.",
            "error"
        )

        return redirect(
            url_for("home") + "#contact"
        )

    with get_db() as conn:

        conn.execute(
            """
            INSERT INTO messages
            (name, email, message)
            VALUES (?, ?, ?)
            """,
            (name, email, message)
        )

        conn.commit()

    flash(
        "Message sent successfully. I'll get back to you soon.",
        "success"
    )

    return redirect(
        url_for("home") + "#contact"
    )


# ADMIN
@app.route("/admin")
@login_required
def admin():

    admin_email = os.environ.get(
        "ADMIN_EMAIL",
        ""
    ).strip().lower()

    current_email = session.get(
        "user_email",
        ""
    ).strip().lower()

    if not admin_email or current_email != admin_email:
        return "Access denied", 403

    with get_db() as conn:

        users = conn.execute(
            """
            SELECT id, name, email, created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

        messages = conn.execute(
            """
            SELECT *
            FROM messages
            ORDER BY id DESC
            """
        ).fetchall()

    return render_template(
        "admin.html",
        users=users,
        messages=messages
    )


# DATABASE
init_db()


# START SERVER
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
