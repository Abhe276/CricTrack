from flask import Flask, render_template, request, redirect, url_for, session 
from db import Database, Batting, BowlingFigures, FieldingStats

app = Flask(__name__)
# session secret key for user authentication - stronger key than gtg from the tutorial 

app.secret_key = "crictrack_secretkey_276"

DB_PATH = ".database/crictrack.db"

# Authentication check
# True if the user is logged in, False otherwise

def authentication_check():
    return session.get("id") is not None

 
 # Home page route
@app.route("/")
def index():
    return render_template("index.html")

# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if authentication_check():
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()

        if not username or not password:
            error = "All fields are required."
        else: 
            db = Database(DB_PATH)
            success = db.RegisterUser(username,password)
            if success:
                import sqlite3
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                user = conn.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
                conn.close()
                session["id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
            else:
                error = "username already exists."

    return render_template("register.html", error=error)


# Login route 
@app.route("/login", methods=["GET", "POST"])
def login():
    if authentication_check():
        return redirect(url_for("index"))
    error = None
    if request.method =="POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        db = Database(DB_PATH)
        user = db.CheckLogin(username, password)

        if user is None:
            error = "Invalid username or password."
        else: 
            session["id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
    return render_template("login.html", error=error)


# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index")) 

# Batting records route
@app.route("/add-batting", methods=["GET", "POST"])
def add_batting():
    if not authentication_check():
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        format = request.form.get("format","").strip()
        runs = request.form.get("runs","").strip()  
        balls = request.form.get("balls","").strip()
        not_out = 1 if request.form.get("not_out") else 0
        if not date or not format or not runs or not balls:
            error = "All fields are required."
        else:
            db = Database(DB_PATH)
            batting = Batting(db)
            batting.AddBatting(session["id"], date, format, int(runs), int(balls), not_out)
            return redirect(url_for("index"))
    return render_template("add_batting.html", error=error) 

# Bowling records route
@app.route("/add-bowling", methods=["GET", "POST"])
def add_bowling():
    if not authentication_check():
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        format = request.form.get("format","").strip()
        overs = request.form.get("overs","").strip()
        runs_given = request.form.get("runs_given","").strip()
        wickets = request.form.get("wickets","").strip()

        if not date or not format or not overs or not runs_given or not wickets:
            error = "All fields are required."
        else:
            db = Database(DB_PATH)
            bowling = BowlingFigures(db)
            bowling.AddBowling(session["id"], date, format, float(overs), int(runs_given), int(wickets))
            return redirect(url_for("index"))
    return render_template("add_bowling.html", error=error)
    
# Fielding records route
@app.route("/add-fielding", methods=["GET", "POST"])
def add_fielding():
    if not authentication_check():
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        catches = request.form.get("catches","").strip()
        run_outs = request.form.get("run_outs","").strip()

        if not date or not catches or not run_outs:
            error = "All fields are required."
        else:
            db = Database(DB_PATH)
            fielding = FieldingStats(db)
            fielding.AddFielding(session["id"], date, int(catches), int(run_outs))
            return redirect(url_for("index"))
    return render_template("add_fielding.html", error=error)
    
# History route to display all records and stats
@app.route("/history")
def history():
    if not authentication_check():
        return redirect(url_for("login"))
    
    uid = session["id"]
    db = Database(DB_PATH)
    batting = Batting(db).GetAllBatting(uid)
    db = Database(DB_PATH)
    bowling = BowlingFigures(db).GetAllBowling(uid)
    db = Database(DB_PATH)
    fielding = FieldingStats(db).GetAllFielding(uid)

    return render_template("history.html", batting=batting, bowling=bowling, fielding=fielding)

# Dashboard route to display stats
@app.route("/dashboard")
def dashboard():
    if not authentication_check():
        return redirect(url_for("login"))
    
    uid = session["id"]
    db = Database(DB_PATH)
    batting_stats = Batting(db).CalcBattingStats(uid)
    db = Database(DB_PATH)
    bowling_stats = BowlingFigures(db).CalcBowlingStats(uid)
    db = Database(DB_PATH)
    fielding_stats = FieldingStats(db).CalcFieldingStats(uid)

    return render_template("dashboard.html", batting_stats=batting_stats, bowling_stats=bowling_stats, fielding_stats=fielding_stats)

# Edit batting record route
@app.route("/edit-batting/<int:record_id>", methods=["GET", "POST"])
def edit_batting(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    record=Batting(db).GetOneBatting(record_id, session["id"])
    if record is None:
        return redirect(url_for("history"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        format = request.form.get("format","").strip()
        runs = request.form.get("runs","").strip()  
        balls = request.form.get("balls","").strip()
        not_out = 1 if request.form.get("not_out") else 0

        if not date or not format or not runs or not balls: 
            error = "All fields are required."
        else: 
            db2 = Database(DB_PATH)
            Batting(db2).EditBatting(record_id, session["id"], date, format, int(runs), int(balls), not_out)
            return redirect(url_for("history"))
    return render_template("edit.html", record=record, record_type="batting", error=error) 
    
# Edit bowling record route
@app.route("/edit-bowling/<int:record_id>", methods=["GET", "POST"])
def edit_bowling(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    record = BowlingFigures(db).GetOneBowling(record_id, session["id"])
    if record is None:
        return redirect(url_for("history"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        format = request.form.get("format","").strip()  
        overs = request.form.get("overs","").strip()        
        runs_given = request.form.get("runs_given","").strip()   
        wickets = request.form.get("wickets","").strip()    

        if not date or not format or not overs or not runs_given or not wickets:
            error = "All fields are required."
        else:
            db2 = Database(DB_PATH)
            BowlingFigures(db2).EditBowling(record_id, session["id"], date, format, float(overs), int(runs_given), int(wickets))
            return redirect(url_for("history"))  
    return render_template("edit.html", record=record, record_type="bowling", error=error) 
    
# Edit fielding record route
@app.route("/edit-fielding/<int:record_id>", methods=["GET", "POST"])
def edit_fielding(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    record = FieldingStats(db).GetOneFielding(record_id, session["id"])
    if record is None:
        return redirect(url_for("history"))
    error = None
    if request.method == "POST":
        date = request.form.get("date","").strip()
        catches = request.form.get("catches","").strip()
        run_outs = request.form.get("run_outs","").strip()

        if not date or not catches or not run_outs:
            error = "All fields are required."
        else:
            db2 = Database(DB_PATH)
            FieldingStats(db2).EditFielding(record_id, session["id"], date, int(catches), int(run_outs))
            return redirect(url_for("history"))
    return render_template("edit.html", record=record, record_type="fielding", error=error)

# Delete batting record route
@app.route("/delete-batting/<int:record_id>")
def delete_batting(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    Batting(db).DeleteBatting(record_id, session["id"])
    return redirect(url_for("history"))

# Delete bowling record route
@app.route("/delete-bowling/<int:record_id>")
def delete_bowling(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    BowlingFigures(db).DeleteBowling(record_id, session["id"])
    return redirect(url_for("history"))

# Delete fielding record route
@app.route("/delete-fielding/<int:record_id>")
def delete_fielding(record_id):
    if not authentication_check():
        return redirect(url_for("login"))
    db = Database(DB_PATH)
    FieldingStats(db).DeleteFielding(record_id, session["id"])
    return redirect(url_for("history"))

if __name__ == "__main__":
    app.run(debug=True)