from flask import Flask, render_template, request, redirect, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from zxcvbn import zxcvbn
from functools import wraps
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

# confirgure the flask app
app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")


# connect the database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("database/salary.db")
        g.db.row_factory = sqlite3.Row
    
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def format_money(amount):
    if amount == int(amount):
        return f"{amount:,.0f}"
    return f"{amount:,.2f}"

def format_dashboard_money(amount):
    return f"{amount:,.0f}"

app.jinja_env.filters["money"] = format_money
app.jinja_env.filters["dashboard_money"] = format_dashboard_money


@app.route("/")
@login_required
def index():
    db = get_db()
    username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    today = date.today()
    current_month = today.strftime("%Y-%m")
    current_year = today.strftime("%Y")
    user_id = session["user_id"]

    month_earning = db.execute("SELECT COALESCE(SUM(quantity * rate_per_unit), 0) FROM income_records WHERE user_id = ? AND strftime('%Y-%m', date) = ?", (user_id, current_month)).fetchone()[0]
    year_earning = db.execute("SELECT COALESCE(SUM(quantity * rate_per_unit), 0) FROM income_records WHERE user_id = ? AND strftime('%Y', date) = ?", (user_id, current_year)).fetchone()[0]

    count = db.execute("SELECT count(*) FROM income_records WHERE user_id = ?", (user_id,)).fetchone()[0]

    average = db.execute("SELECT COALESCE(AVG(quantity * rate_per_unit), 0) FROM income_records WHERE user_id = ?", (user_id,)).fetchone()[0]

    transactions = db.execute("SELECT * FROM income_records WHERE user_id = ? ORDER BY date DESC, id DESC", (user_id,)).fetchall()


    return render_template("index.html", username=username["username"], month_earning=month_earning, year_earning=year_earning, count=count, average=average, transactions=transactions)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", error="Missing username")
        if not password:
            return render_template("login.html", error="Missing password")

        db = get_db()
        user = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            return render_template("login.html", error="Invalid password or username")
        if not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid password or username")
        
        session.clear()
        session["user_id"] = user["id"]

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("register.html", error="Username is required")

        if not password:
            return render_template("register.html", error="Password is required")
        

        if not confirmation:
            return render_template("register.html", error="Confirmation is required")

        if password != confirmation:
            return render_template("register.html", error="Password did not match")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters")

        result = zxcvbn(password)
        if result["score"] < 3:
            return render_template("register.html", error="Password is too weak")

        password_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)", (username, password_hash))
            db.commit()
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists")
        
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"]) 
@login_required       
def add():
    if request.method == "POST":
        # Retrieve form data
        income_type = request.form.get("income_type", "").strip()
        description = request.form.get("description", "").strip() or None
        record_date = request.form.get("date", "").strip()
        quantity = request.form.get("quantity", "").strip()
        rate_per_unit = request.form.get("rate_per_unit", "").strip()

        # Check whether required fields are filled
        if not income_type or not record_date or not quantity or not rate_per_unit:
            return render_template("add.html", error="Please fill in all required fields.")

        valid_income = ["Teaching", "Freelance", "Event", "Other"]

        # Validate income type
        if income_type not in valid_income:
            return render_template("add.html", error="Invalid income category.")
        
        # Validate date
        try:
            date.fromisoformat(record_date)
        except ValueError:
            return render_template("add.html", error="Please enter a valid date.")

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return render_template("add.html", error="Quantity must be a positive integer. ")

        # Validate rate per unit
        try:
            rate_per_unit = Decimal(rate_per_unit)

            if not rate_per_unit.is_finite() or rate_per_unit <= 0:
                raise ValueError

            # Only two decimal places
            if rate_per_unit.as_tuple().exponent < -2:
                raise ValueError

            rate_per_unit = int(rate_per_unit * 100)
        except (InvalidOperation, ValueError):
            print("Validation failed: invalid rate")
            return render_template("add.html", error="Please enter valid rate (e.g 25.00)")

        # Open database
        db = get_db()
        user_id = session["user_id"]

        try:
            db.execute("INSERT INTO income_records(user_id, date, income_type, description, quantity, rate_per_unit) VALUES (?, ?, ?, ?, ?, ?)", (user_id, record_date, income_type, description, quantity, rate_per_unit))
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            print(e)
            return render_template("add.html", error="Adding failed. Try again")

        return redirect("/")

    else:
        return render_template("add.html")

@app.route("/records")
@login_required
def records():
    # receive form data
    category = request.args.get("category") or None
    month = request.args.get("month") or None
    search = request.args.get("search") or None
    sort = request.args.get("sort") or "newest"

    # checking which query
    db = get_db()
    user_id = session["user_id"]

    query = """
        SELECT * FROM income_records
        WHERE user_id = ?
    """

    params = [user_id]

    if category:
        query += " AND income_type = ?"
        params.append(category)

    if month:
        query += " AND strftime('%m', date) = ?"
        params.append(month)
    
    if search:
        query += " AND description LIKE ?"
        params.append(f"%{search}%")

    sorts = {
        "newest": " date DESC",
        "oldest": " date ASC",
        "highest": " (quantity * rate_per_unit) DESC",
        "lowest": " (quantity * rate_per_unit) ASC"
    }

    query += f"ORDER BY {sorts[sort]}"
    

    records = db.execute(query, params).fetchall()

    months = [
    ("01", "January"),
    ("02", "February"),
    ("03", "March"),
    ("04", "April"),
    ("05", "May"),
    ("06", "June"),
    ("07", "July"),
    ("08", "August"),
    ("09", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December")
]

    categories = [
        "Teaching",
        "Freelance",
        "Event",
        "Other"
    ]

    return render_template("records.html", records=records, categories=categories, category=category, months=months ,month=month, search=search, sort=sort)

@app.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete(record_id):
    db = get_db()
    user_id = session["user_id"]
    result = db.execute("DELETE FROM income_records WHERE id = ? AND user_id = ?", (record_id, user_id))
    db.commit()

    if result.rowcount != 1:
        print("delete failed")

    return redirect("/records")

@app.route("/edit/<int:record_id>", methods=["POST"])
@login_required
def edit(record_id):
    # Retrieve form data
    income_type = request.form.get("income_type", "").strip()
    description = request.form.get("description", "").strip() or None
    record_date = request.form.get("date", "").strip()
    quantity = request.form.get("quantity", "").strip()
    rate_per_unit = request.form.get("rate_per_unit", "").strip()

    # Check whether required fields are filled
    if not income_type or not record_date or not quantity or not rate_per_unit:
        return render_template("records.html", error="Please fill in all required fields.")

    valid_income = ["Teaching", "Freelance", "Event", "Other"]

    # Validate income type
    if income_type not in valid_income:
        return render_template("records.html", error="Invalid income category.")
    
    # Validate date
    try:
        date.fromisoformat(record_date)
    except ValueError:
        return render_template("records.html", error="Please enter a valid date.")

    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return render_template("records.html", error="Quantity must be a positive integer. ")

    # Validate rate per unit
    try:
        rate_per_unit = Decimal(rate_per_unit)

        if not rate_per_unit.is_finite() or rate_per_unit <= 0:
            raise ValueError

        # Only two decimal places
        if rate_per_unit.as_tuple().exponent < -2:
            raise ValueError

        rate_per_unit = int(rate_per_unit * 100)
    except (InvalidOperation, ValueError):
        print("Validation failed: invalid rate")
        return render_template("records.html", error="Please enter valid rate (e.g 25.00)")

    # Open database
    db = get_db()
    user_id = session["user_id"]

    try:
        db.execute("UPDATE income_records SET date = ?, income_type = ?, description = ?, quantity = ?, rate_per_unit = ? WHERE id = ? AND user_id = ?", (record_date, income_type, description, quantity, rate_per_unit, record_id, user_id))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        print(e)
        return render_template("records.html", error="Exiting failed. Try again")

    return redirect("/records")



@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")