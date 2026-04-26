-- CricTrack Database Framework 
-- Creates all the tables needed for the PWA

-- Table: users - stored registered users
CREATE TABLE Users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,  
    password TEXT NOT NULL
);

-- Table: Batting - stored batting statistics
-- user_id links each batting record to the user who logged it
CREATE TABLE Batting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    format TEXT NOT NULL,
    runs INTEGER NOT NULL,
    balls INTEGER NOT NULL,
    not_out INTEGER NOT NULL DEFAULT 0, --SQLite does not have a BOOLEAN type, so we use INTEGER (0 or 1)
    FOREIGN KEY (user_id) REFERENCES Users(id) 
);

-- Table: BowlingFigures - stored bowling statistics
CREATE TABLE BowlingFigures(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    format TEXT NOT NULL,
    overs REAL NOT NULL, -- Using REAL to allow for fractional overs
    runs_given INTEGER NOT NULL,    
    wickets INTEGER NOT NULL,   
    FOREIGN KEY (user_id) REFERENCES Users(id) 
);  

-- Table: FieldingStats - stored fielding statistics

CREATE TABLE FieldingStats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    catches INTEGER NOT NULL,
    run_outs INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);


    