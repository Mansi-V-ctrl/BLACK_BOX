from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


app = Flask(__name__)
app.secret_key = "black-box-secret-key"


def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def query_db(query, params=(), fetchone=False, commit=False):
    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)

        if commit:
            conn.commit()
            return True

        return cursor.fetchone() if fetchone else cursor.fetchall()

    except Error as e:
        print("Database Error:", e)
        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def detect_possible_incident(application_id):
    since = datetime.now() - timedelta(minutes=5)

    failed_events = query_db(
        """
        SELECT event_id
        FROM events
        WHERE application_id = %s
        AND status = 'FAILED'
        AND event_time >= %s
        ORDER BY event_time
        """,
        (application_id, since)
    )

    if failed_events and len(failed_events) >= 3:
        return failed_events

    return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        existing = query_db(
            "SELECT user_id FROM users WHERE email = %s",
            (email,),
            fetchone=True
        )

        if existing:
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        query_db(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, password),
            commit=True
        )

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        user = query_db(
            """
            SELECT user_id, name, email
            FROM users
            WHERE email = %s AND password = %s
            """,
            (email, password),
            fetchone=True
        )

        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    recent_events = query_db(
        """
        SELECT e.*, a.name AS application_name
        FROM events e
        JOIN applications a
        ON e.application_id = a.application_id
        ORDER BY e.event_time DESC
        LIMIT 5
        """
    )

    possible_incidents = []

    applications = query_db(
        "SELECT * FROM applications"
    )

    if applications:
        for application in applications:

            failed = detect_possible_incident(
                application["application_id"]
            )

            if failed:
                possible_incidents.append({
                    "application": application["name"],
                    "count": len(failed)
                })

    return render_template(
        "home.html",
        recent_events=recent_events,
        possible_incidents=possible_incidents
    )


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    total_result = query_db(
        "SELECT COUNT(*) AS count FROM events",
        fetchone=True
    )

    open_result = query_db(
        """
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status != 'RESOLVED'
        """,
        fetchone=True
    )

    resolved_result = query_db(
        """
        SELECT COUNT(*) AS count
        FROM incidents
        WHERE status = 'RESOLVED'
        """,
        fetchone=True
    )

    failed_result = query_db(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE status = 'FAILED'
        """,
        fetchone=True
    )

    total_events = total_result["count"] if total_result else 0
    open_incidents = open_result["count"] if open_result else 0
    resolved_incidents = resolved_result["count"] if resolved_result else 0
    failed_events = failed_result["count"] if failed_result else 0

    status_data = query_db(
        """
        SELECT status, COUNT(*) AS count
        FROM events
        GROUP BY status
        """
    ) or []

    severity_data = query_db(
        """
        SELECT severity, COUNT(*) AS count
        FROM incidents
        GROUP BY severity
        """
    ) or []

    return render_template(
        "dashboard.html",
        total_events=total_events,
        open_incidents=open_incidents,
        resolved_incidents=resolved_incidents,
        failed_events=failed_events,
        status_data=status_data,
        severity_data=severity_data
    )


@app.route("/events")
def events():
    if "user_id" not in session:
        return redirect(url_for("login"))

    events_data = query_db(
        """
        SELECT e.*,
               a.name AS application_name,
               u.name AS user_name
        FROM events e
        JOIN applications a
        ON e.application_id = a.application_id
        LEFT JOIN users u
        ON e.user_id = u.user_id
        ORDER BY e.event_time DESC
        """
    )

    return render_template(
        "events.html",
        events=events_data
    )


@app.route("/demo")
def demo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("demo.html")


@app.route("/demo/generate", methods=["POST"])
def generate_demo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    application = query_db(
        """
        SELECT application_id
        FROM applications
        WHERE name = 'Demo Payment App'
        """,
        fetchone=True
    )

    if not application:
        flash("Demo application not found.", "error")
        return redirect(url_for("demo"))

    events = [
        (
            "Login",
            "SUCCESS",
            "User logged into the demo application."
        ),
        (
            "Payment Open",
            "SUCCESS",
            "Payment section opened."
        ),
        (
            "Transaction Start",
            "SUCCESS",
            "Transaction started."
        ),
        (
            "API Request",
            "SUCCESS",
            "API request sent."
        ),
        (
            "API Timeout",
            "FAILED",
            "API request timed out."
        ),
        (
            "Retry",
            "FAILED",
            "Transaction retry failed."
        ),
        (
            "Payment Failed",
            "FAILED",
            "Payment transaction failed."
        )
    ]

    for event_name, status, description in events:

        query_db(
            """
            INSERT INTO events
            (
                application_id,
                user_id,
                event_type,
                status,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                application["application_id"],
                session["user_id"],
                event_name,
                status,
                description
            ),
            commit=True
        )

    flash(
        "Demo transaction completed. 7 events captured.",
        "success"
    )

    return redirect(url_for("demo"))


@app.route("/incidents")
def incidents():
    if "user_id" not in session:
        return redirect(url_for("login"))

    incidents_data = query_db(
        """
        SELECT i.*,
               a.name AS application_name,
               u.name AS creator_name
        FROM incidents i
        JOIN applications a
        ON i.application_id = a.application_id
        LEFT JOIN users u
        ON i.created_by = u.user_id
        ORDER BY i.created_at DESC
        """
    )

    applications = query_db(
        "SELECT * FROM applications"
    )

    possible_incidents = []

    if applications:
        for application in applications:

            failed = detect_possible_incident(
                application["application_id"]
            )

            if failed:
                possible_incidents.append({
                    "application_id": application["application_id"],
                    "application": application["name"],
                    "count": len(failed)
                })

    return render_template(
        "incidents.html",
        incidents=incidents_data,
        possible_incidents=possible_incidents
    )


@app.route("/incidents/create", methods=["POST"])
def create_incident():
    if "user_id" not in session:
        return redirect(url_for("login"))

    application_id = request.form["application_id"]

    failed_events = detect_possible_incident(
        application_id
    )

    if len(failed_events) < 3:
        flash(
            "Not enough failed events to create an incident.",
            "error"
        )
        return redirect(url_for("incidents"))

    query_db(
        """
        INSERT INTO incidents
        (
            application_id,
            title,
            description,
            severity,
            status,
            created_by
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            application_id,
            "Payment API Failure Pattern",
            "Multiple failed events detected within a short time window.",
            "HIGH",
            "OPEN",
            session["user_id"]
        ),
        commit=True
    )

    incident = query_db(
        "SELECT LAST_INSERT_ID() AS incident_id",
        fetchone=True
    )

    if not incident:
        flash(
            "Incident could not be created.",
            "error"
        )
        return redirect(url_for("incidents"))

    new_incident_id = incident["incident_id"]

    for event in failed_events:

        query_db(
            """
            INSERT INTO incident_events
            (
                incident_id,
                event_id
            )
            VALUES (%s, %s)
            """,
            (
                new_incident_id,
                event["event_id"]
            ),
            commit=True
        )

    flash(
        "Incident created successfully.",
        "success"
    )

    return redirect(
        url_for(
            "incident_detail",
            incident_id=new_incident_id
        )
    )


@app.route("/incidents/<int:incident_id>")
def incident_detail(incident_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    incident = query_db(
        """
        SELECT i.*,
               a.name AS application_name
        FROM incidents i
        JOIN applications a
        ON i.application_id = a.application_id
        WHERE i.incident_id = %s
        """,
        (incident_id,),
        fetchone=True
    )

    if not incident:
        return redirect(url_for("incidents"))

    timeline = query_db(
        """
        SELECT e.*
        FROM events e
        JOIN incident_events ie
        ON e.event_id = ie.event_id
        WHERE ie.incident_id = %s
        ORDER BY e.event_time
        """,
        (incident_id,)
    )

    resolution_data = query_db(
        """
        SELECT r.*,
               u.name AS resolver_name
        FROM resolutions r
        LEFT JOIN users u
        ON r.resolved_by = u.user_id
        WHERE r.incident_id = %s
        """,
        (incident_id,),
        fetchone=True
    )

    return render_template(
        "incident_detail.html",
        incident=incident,
        timeline=timeline,
        resolution=resolution_data
    )


@app.route(
    "/incidents/<int:incident_id>/investigate",
    methods=["POST"]
)
def investigate_incident(incident_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    query_db(
        """
        UPDATE incidents
        SET status = 'UNDER INVESTIGATION'
        WHERE incident_id = %s
        """,
        (incident_id,),
        commit=True
    )

    flash(
        "Investigation started.",
        "success"
    )

    return redirect(
        url_for(
            "incident_detail",
            incident_id=incident_id
        )
    )


@app.route(
    "/incidents/<int:incident_id>/resolve",
    methods=["GET", "POST"]
)
def resolution(incident_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        root_cause = request.form["root_cause"]
        resolution_text = request.form["resolution"]

        query_db(
            """
            INSERT INTO resolutions
            (
                incident_id,
                root_cause,
                resolution,
                resolved_by,
                resolved_at
            )
            VALUES (%s, %s, %s, %s, NOW())

            ON DUPLICATE KEY UPDATE
                root_cause = VALUES(root_cause),
                resolution = VALUES(resolution),
                resolved_by = VALUES(resolved_by),
                resolved_at = NOW()
            """,
            (
                incident_id,
                root_cause,
                resolution_text,
                session["user_id"]
            ),
            commit=True
        )

        query_db(
            """
            UPDATE incidents
            SET status = 'RESOLVED'
            WHERE incident_id = %s
            """,
            (incident_id,),
            commit=True
        )

        flash(
            "Incident resolved successfully.",
            "success"
        )

        return redirect(
            url_for(
                "incident_detail",
                incident_id=incident_id
            )
        )

    incident = query_db(
        """
        SELECT *
        FROM incidents
        WHERE incident_id = %s
        """,
        (incident_id,),
        fetchone=True
    )

    if not incident:
        return redirect(url_for("incidents"))

    return render_template(
        "resolution.html",
        incident=incident
    )


if __name__ == "__main__":
    app.run(debug=True)