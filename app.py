from flask import Flask, render_template,redirect, url_for, request,session
import mysql.connector



app = Flask(__name__)
app.secret_key = "studysphere_secret_key"
ADMIN_EMAIL = "manojkumarmanojkumar08758@gmail.com"

# ---------------- DATABASE ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="studysphere",
        password="studysphere123",
        database="studysphere_db"
    )

# ---------------- UPLOAD (ADMIN) ----------------
@app.route("/admin")
def admin():
    return redirect("/admin/upload")
@app.route("/admin/upload", methods=["GET", "POST"])
def admin_upload():

    # 🔐 Check admin access
        # ✅ ALWAYS create DB & cursor first
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ---------------- HANDLE FORM SUBMIT ----------------
    if request.method == "POST":
        category = request.form["category"]
        branch = request.form.get("branch")
        sem = request.form.get("sem")
        title = request.form["title"]
        file_url = request.form["file_url"]
        # Materials & Papers have branch + sem
        if category in ["materials", "papers"]:
            cursor.execute("""
                INSERT INTO materials (category, branch, sem, title, file_url)
                VALUES (%s, %s, %s, %s, %s)
            """, (category, branch, sem, title, file_url))

        # Others only need category + title + link
        else:
            cursor.execute("""
                INSERT INTO resources (category, title, drive_link)
                VALUES (%s, %s, %s)
            """, (category, title, file_url))
          
            db.commit()
     # 🔽 FETCH UPLOAD HISTORY
    cursor.execute("""
    SELECT * FROM resources
    ORDER BY created_at DESC
""")

    uploads = cursor.fetchall()

    # ✅ CLOSE PROPERLY
    cursor.close()
    db.close()

    return render_template("admin_upload.html", uploads=uploads)
        
    return "✅ Uploaded Successfully"

@app.route("/admin/delete/<int:id>")
def delete_resource(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM materials WHERE id = %s", (id,))
    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("admin_upload"))

    
@app.route("/admin/users")
def admin_users():

    # 🔐 Check admin access
    user_email = request.args.get("email")

    if user_email != ADMIN_EMAIL:
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT email, name, registered_at
        FROM users
        ORDER BY registered_at DESC
    """)

    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return render_template(
        "admin_users.html",
        users=users,
        total_users=total_users
    )

# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    q = request.args.get("q")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 🔎 Search in resources
    cursor.execute("""
        SELECT title, drive_link AS link
        FROM resources
        WHERE title LIKE %s
    """, (f"%{q}%",))

    resource_results = cursor.fetchall()

    # 🔎 Search in materials
    cursor.execute("""
        SELECT title, file_url AS link
        FROM materials
        WHERE title LIKE %s
    """, (f"%{q}%",))

    material_results = cursor.fetchall()

    results = resource_results + material_results

    cursor.close()
    db.close()

    return render_template("search.html", results=results, q=q)
# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


    
# ---------------- RESOURCES ----------------
@app.route("/resource")
def resource_page():
    
    return render_template("resource.html")

# ---------------- MATERIALS ----------------
@app.route("/materials")
def materials():
    return render_template("materials.html")

@app.route("/materials/<branch>")
def materials_branch(branch):
    return render_template("materials_branch.html", branch=branch)

@app.route("/materials/<branch>/<int:sem>")
def materials_sem(branch, sem):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, file_url
        FROM materials
        WHERE category=%s AND branch=%s AND sem=%s
    """, ("materials", branch, sem))

    pdfs = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "materials_subjects.html",
        pdfs=pdfs,
        branch=branch,
        sem=sem
    )
# ---------------- VIDEOS ----------------
@app.route("/videos")
def videos():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, drive_link
        FROM resources
        WHERE category = 'videos'
    """)

    videos = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("videos.html", videos=videos)

# ---------------- PAPERS ----------------
@app.route("/papers")
def papers():
    return render_template("papers.html")

@app.route("/papers/<branch>")
def papers_branch(branch):
    return render_template("papers_branch.html", branch=branch)

@app.route("/papers/<branch>/<int:sem>")
def papers_sem(branch, sem):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, drive_link
        FROM resources
        WHERE category='papers'
        AND branch=%s
        AND semester=%s
    """, (branch, sem))

    files = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("papers_sem.html", files=files, branch=branch, sem=sem)
# ---------------- APTITUDE ----------------
@app.route("/aptitude")
def aptitude():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, drive_link
        FROM resources
        WHERE category='aptitude'
    """)

    aptitude = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("aptitude.html", aptitude=aptitude)

# ---------------- CODING ----------------
@app.route("/coding")
def coding():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, drive_link
        FROM resources
        WHERE category='coding'
    """)

    coding = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("coding.html", coding=coding)
# ---------------- INTERVIEW ----------------
@app.route("/interview")
def interview():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, drive_link
        FROM resources
        WHERE category='interview'
    """)

    interviews = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("interview.html", interviews=interviews)

# ---------------- LOGOUT --------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
# --------------- USER DETAILS --------------

@app.route("/save-user", methods=["POST"])
def save_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"status": "error", "message": "Missing data"}, 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT IGNORE INTO users (name, email)
        VALUES (%s, %s)
    """, (name, email))

    db.commit()
    cursor.close()
    db.close()

    return {"status": "saved"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
