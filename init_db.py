import sqlite3
from config import DATABASE


# connect to database
db = sqlite3.connect(DATABASE)
cursor = db.cursor()

# read sql file
with open("database/schema.sql", "r") as sql_file:
    sql_script = sql_file.read()

try:
    cursor.executescript(sql_script)
    db.commit()
    print("Database succesfully created")
except sqlite3.Error as e:
    print(f"An error has occured: {e}")
finally:
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    print(cursor.fetchall())
    db.close()


