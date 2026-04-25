import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Database Class
# Handles the database connection and user authentication

class Database: 
    def __init__(self,filepath):                         # Stroes the path to the database file
        self.filepath = filepath
        self.connection = None

    def GetDB(self):                                     # Establishes a connection to the database and returns it                                  
        self.connection = sqlite3.connect(self.filepath)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def CloseDB(self):                                   # closes the connection when done
        if self.connection:
            self.connection.close()
            
    def RegisterUser(self, username, password):          # Hash the password using scrypt
        hashed = generate_password_hash(password)
        try:
            conn = self.GetDB()
            conn.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False                           # Username already exists - unique usermame
        finally:
            self.CloseDB()


    def CheckLogin(self, username, password):            # Finds the user in the database and checks if the password is correct
        try:
            conn = self.GetDB()
            user = conn.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
            if user is None: 
                return None
            if check_password_hash(user['password'], password):
                return user
            return None 
        finally:
            self.CloseDB()  


# Batting Class
# handle all the batting related database operations
class Batting:
    def __init__(self, db):
        self.db = db
    def AddBatting(self, user_id, date, format, runs, balls, not_out):
        try:
            conn = self.db.GetDB()
            conn.execute("INSERT INTO Batting (user_id, date, format, runs, balls, not_out) VALUES (?, ?, ?, ?, ?, ?)", 
                         (user_id, date, format, runs, balls, not_out))
            conn.commit()
            return True
        finally:
            self.db.CloseDB()
    def GetAllBatting(self, user_id):
        # Links batting records to the user and returns all batting records for that user
        try:
            conn = self.db.GetDB()
            rows = conn.execute("SELECT Batting.*, Users.username FROM Batting JOIN Users ON Batting.user_id = Users.id WHERE Batting.user_id = ? ORDER BY Batting.date DESC", (user_id,)).fetchall()
            return rows
        finally:
            self.db.CloseDB()
    def GetOneBatting(self, record_id, user_id):
        # Retrieves a single batting record based on the user ID and record ID verifiers ownership
        try:
            conn = self.db.GetDB()
            row = conn.execute("SELECT * FROM Batting WHERE id = ? AND user_id = ?", (record_id, user_id)).fetchone()
            return row
        finally:
            self.db.CloseDB()
    def EditBatting(self, record_id, user_id, date, format, runs, balls, not_out):
        # Updates a batting record if the user owns it
        try:
            conn = self.db.GetDB()
            conn.execute("UPDATE Batting SET date = ?, format = ?, runs = ?, balls = ?, not_out = ? WHERE id = ? AND user_id = ?", 
                         (date, format, runs, balls, not_out, record_id, user_id))
            conn.commit()
            return True
        finally:
            self.db.CloseDB()

    def DeleteBatting(self, record_id, user_id):
        # Delete a batting record if the user owns it
        try:
            conn = self.db.GetDB()
            conn.execute("DELETE FROM Batting WHERE id = ? AND user_id = ?", (record_id, user_id))
            conn.commit()
            return True 
        finally:
            self.db.CloseDB()

    def CalcBattingStats(self, user_id):
        # Selects all the batting records and calculate stats from them
        try: 
            conn = self.db.GetDB()
            rows = conn.execute("SELECT * FROM Batting WHERE user_id = ?", (user_id,)).fetchall()
            if not rows:
                return None
            total_runs = sum(row["runs"] for row in rows)
            total_balls = sum(row["balls"] for row in rows)
            dismissals = sum(1 for row in rows if row["not_out"] == 0)
            highest = max(row["runs"] for row in rows) 
            batting_avg = round(total_runs/dismissals, 2) if dismissals>0 else total_runs
            strike_rate = round((total_runs/total_balls)*100, 2) if total_balls>0 else 0
            return {
                "innings": len(rows),
                "total_runs": total_runs,
                "batting_avg": batting_avg,
                "strike_rate": strike_rate, 
                "highest": highest,
            }
        finally:
            self.db.CloseDB()

#BowlingFigures Class
# Handles all the bowling related database operations
class BowlingFigures:
    def __init__(self, db):
        self.db = db
    def AddBowling(self, user_id, date, format, overs, runs_given, wickets):
        try:
            conn = self.db.GetDB()
            conn.execute("INSERT INTO BowlingFigures (user_id, date, format, overs, runs_given, wickets) VALUES (?, ?, ?, ?, ?, ?)", 
                         (user_id, date, format, overs, runs_given, wickets))
            conn.commit()
            return True
        finally:
            self.db.CloseDB()
    
    def GetAllBowling(self, user_id):
        # Links bowling records to the user and returns all bowling records for that user
        try:
            conn = self.db.GetDB()
            rows = conn.execute("SELECT BowlingFigures.*, Users.username FROM BowlingFigures JOIN Users ON BowlingFigures.user_id = Users.id WHERE BowlingFigures.user_id = ? ORDER BY BowlingFigures.date DESC", (user_id,)).fetchall()
            return rows
        finally:
            self.db.CloseDB()   

    def GetOneBowling(self, record_id, user_id):
        # Retrieves a single bowling record based on the user ID and record ID verifiers ownership
        try:
            conn = self.db.GetDB()
            row = conn.execute("SELECT * FROM BowlingFigures WHERE id = ? AND user_id = ?", (record_id, user_id)).fetchone()
            return row
        finally:
            self.db.CloseDB()

    def EditBowling(self, record_id, user_id, date, format, overs, runs_given, wickets):
        # Updates a bowling record if the user owns it
        try:
            conn = self.db.GetDB()
            conn.execute("UPDATE BowlingFigures SET date = ?, format = ?, overs = ?, runs_given = ?, wickets = ? WHERE id = ? AND user_id = ?", 
                         (date, format, overs, runs_given, wickets, record_id, user_id)) 
            conn.commit()
            return True
        finally:
            self.db.CloseDB()
    
    def DeleteBowling(self, record_id, user_id):
        # Delete a bowling record if the user owns it
        try:
            conn = self.db.GetDB()
            conn.execute("DELETE FROM BowlingFigures WHERE id = ? AND user_id = ?", (record_id, user_id))
            conn.commit()
            return True 
        finally:
            self.db.CloseDB()
    
    def CalcBowlingStats(self, user_id):
        # Selects all the bowling records and calculate stats from them
        try: 
            conn = self.db.GetDB()
            rows = conn.execute("SELECT * FROM BowlingFigures WHERE user_id = ?", (user_id,)).fetchall()
            if not rows:
                return None
            total_wickets = sum(row["wickets"] for row in rows)
            total_runs_given = sum(row["runs_given"] for row in rows)
            total_overs = sum(row["overs"] for row in rows)
            bowling_avg = round(total_runs_given/total_wickets, 2) if total_wickets>0 else "N/A"
            economy = round(total_runs_given/total_overs, 2) if total_overs>0 else 0
            return {
                "matches": len(rows),
                "total_wickets": total_wickets,
                "bowling_avg": bowling_avg,
                "economy": economy,
            }   
        finally:
            self.db.CloseDB()   

# FieldingStats Class
# Handles all the fielding related database operations  
class FieldingStats:
    def __init__(self, db):
        self.db = db
    def AddFielding(self, user_id, date, catches, run_outs):
        try:
            conn = self.db.GetDB()
            conn.execute("INSERT INTO FieldingStats (user_id, date, catches, run_outs) VALUES (?, ?, ?, ?)", 
                         (user_id, date, catches, run_outs))    
            conn.commit()
            return True
        finally:
            self.db.CloseDB()

    def GetAllFielding(self, user_id):
        # Links fielding records to the user and returns all fielding records for that user
        try:
            conn = self.db.GetDB()
            rows = conn.execute("SELECT FieldingStats.*, Users.username FROM FieldingStats JOIN Users ON FieldingStats.user_id = Users.id WHERE FieldingStats.user_id = ? ORDER BY FieldingStats.date DESC", (user_id,)).fetchall()
            return rows
        finally:
            self.db.CloseDB()

    def GetOneFielding(self, record_id, user_id):         
        # Retrieves a single fielding record based on the user ID and record ID verifiers ownership
        try:
            conn = self.db.GetDB()
            row = conn.execute("SELECT * FROM FieldingStats WHERE id = ? AND user_id = ?", (record_id, user_id)).fetchone()
            return row
        finally:
            self.db.CloseDB()
    
    def EditFielding(self, record_id, user_id, date, catches, run_outs):
        try:
            conn = self.db.GetDB()
            conn.execute("UPDATE FieldingStats SET date = ?, catches = ?, run_outs = ? WHERE id = ? AND user_id = ?", 
                         (date, catches, run_outs, record_id, user_id))
            conn.commit()
            return True
        finally:
            self.db.CloseDB()

    def DeleteFielding(self, record_id, user_id):
        try:
            conn = self.db.GetDB()
            conn.execute("DELETE FROM FieldingStats WHERE id = ? AND user_id = ?", (record_id, user_id))
            conn.commit()
            return True 
        finally:
            self.db.CloseDB()
    
    def CalcFieldingStats(self, user_id):  
        # Selects all the fielding records and calculate stats from them
        try: 
            conn = self.db.GetDB()
            rows = conn.execute("SELECT * FROM FieldingStats WHERE user_id = ?", (user_id,)).fetchall()
            if not rows:
                return None
            total_catches = sum(row["catches"] for row in rows)
            total_run_outs = sum(row["run_outs"] for row in rows)
            return {
                "matches": len(rows),
                "total_catches": total_catches,
                "total_run_outs": total_run_outs,
            }   
        finally:
            self.db.CloseDB()
    
    