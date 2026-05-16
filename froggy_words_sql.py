import sqlite3

DATA_BASE = "froggy_board.db"

def create_table():
    MAKE_TABLE = '''CREATE TABLE IF NOT EXISTS Leaderboard(
    User_ID INTEGER PRIMARY KEY,
    Wins INTEGER);'''

    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        conn.execute(MAKE_TABLE)
        db.commit()

def reset_leaderboard():
    TRUNCATE_TABLE = '''DELETE FROM Leaderboard;'''

    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        conn.execute(TRUNCATE_TABLE)
        db.commit()

def add_new_member(uid):
    ADD_USER = f'''INSERT INTO Leaderboard VALUES ({uid}, 1);'''

    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        conn.execute(ADD_USER)
        db.commit()

def update_score(uid, score):
    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        UPDATE_SCORE = '''UPDATE Leaderboard SET Wins = ? WHERE User_ID = ?;'''
        VALUES = (score, uid)
        conn.execute(UPDATE_SCORE, VALUES)
        db.commit()

def add_win(uid):
    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        FIND_ROW = '''SELECT Wins FROM Leaderboard WHERE User_ID = ?;'''
        VALUES = (uid,)
        conn.execute(FIND_ROW, VALUES)
        row = conn.fetchone()
    if not row:
        add_new_member(uid)
    else:
        new_score = row[0] + 1
        update_score(uid, new_score)

def get_leaderboard():
    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        GET_LEADERBOARD = '''SELECT * FROM Leaderboard;'''
        conn.execute(GET_LEADERBOARD)
        return conn.fetchall()

def get_user_score(uid):
    with sqlite3.connect(DATA_BASE) as db:
        conn = db.cursor()
        GET_SCORE = '''SELECT Wins FROM Leaderboard WHERE User_ID = ?'''
        VALUES = (uid,)
        conn.execute(GET_SCORE, VALUES)
        row = conn.fetchone()
        return row[0] if row else None


create_table()
