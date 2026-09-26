from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("campussos.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Under Review'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lost_found (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            location TEXT NOT NULL,
            item_type TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit_report", methods=["POST"])
def submit_report():

    data = request.get_json()

    issue_type = data.get("issue_type")
    location = data.get("location")
    description = data.get("description")

    conn = sqlite3.connect("campussos.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports (issue_type, location, description)
        VALUES (?, ?, ?)
    """, (issue_type, location, description))

    report_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "report_id": report_id,
        "status": "Under Review"
    })


@app.route("/track_report/<int:report_id>")
def track_report(report_id):

    conn = sqlite3.connect("campussos.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT issue_type, location, description, status FROM reports WHERE id = ?",
        (report_id,)
    )

    report = cursor.fetchone()
    conn.close()

    if report is None:
        return jsonify({
            "success": False,
            "message": "Report not found."
        })

    return jsonify({
        "success": True,
        "issue_type": report[0],
        "location": report[1],
        "description": report[2],
        "status": report[3]
    })


@app.route("/submit_lost_found", methods=["POST"])
def submit_lost_found():

    data = request.get_json()

    item_name = data.get("item_name")
    location = data.get("location")
    item_type = data.get("item_type")
    description = data.get("description")

    conn = sqlite3.connect("campussos.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lost_found
        (item_name, location, item_type, description)
        VALUES (?, ?, ?, ?)
    """, (item_name, location, item_type, description))

    item_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "item_id": item_id
    })

@app.route("/lost_found")
def get_lost_found():

    conn = sqlite3.connect("campussos.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, item_name, location, item_type, description
        FROM lost_found
        ORDER BY id DESC
    """)

    items = cursor.fetchall()
    conn.close()

    item_list = []

    for item in items:
        item_list.append({
            "id": item[0],
            "item_name": item[1],
            "location": item[2],
            "item_type": item[3],
            "description": item[4]
        })

    return jsonify({
        "success": True,
        "items": item_list
    })
if __name__ == "__main__":
    init_db()
    app.run(debug=True)