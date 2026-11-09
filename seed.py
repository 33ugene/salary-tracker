import sqlite3
from datetime import date, timedelta
import random

for _ in range(200):
    db = sqlite3.connect("database/salary.db")

    today = date.today()
    random_days = random.randint(0, 365)
    random_date = today - timedelta(days=random_days)

    income_types = ["Teaching", "Freelance", "Event", "Other"]
    income_type = random.choice(income_types)

    quantity = random.randint(1, 10)

    rate = random.randint(25, 500) * 100

    db.execute("INSERT INTO income_records(user_id, date, income_type, quantity, rate_per_unit) VALUES (?, ?, ?, ?, ?)", (4, random_date, income_type, quantity, rate))
    db.commit()