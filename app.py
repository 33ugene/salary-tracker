from flask import Flask, render_template, request, redirect, session, g, Response, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from zxcvbn import zxcvbn
from functools import wraps
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
import csv
import io
import secrets

# confirgure the flask app
app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" # Cheap first layer


# connect the database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("database/salary.db")
        g.db.row_factory = sqlite3.Row
    
    return g.db

DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(32))

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()

@app.before_request
def check_csrf():
    if request.method == "POST":
        sent = request.form.get("csrf_token", "").encode()
        expected = session.get("csrf_token", "").encode()
        if not expected or not secrets.compare_digest(sent, expected):
            abort(400)

@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["csrf_token"]}


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

def sanitize_csv_value(value):
    if value is None:
        return ""
    
    value = str(value)

    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + value

    return value

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

    transactions = db.execute("SELECT * FROM income_records WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 10", (user_id,)).fetchall()


    return render_template("index.html", username=username["username"], month_earning=month_earning, year_earning=year_earning, count=count, average=average, transactions=transactions)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username") or ""
        password = request.form.get("password")

        username = username[:64].strip().lower()

        if len(username) > 64:
            return render_template("login.html", error="Username is too long")

        if not username:
            return render_template("login.html", error="Missing username")

        if not password:
            return render_template("login.html", error="Missing password")

        db = get_db()

        WINDOW, MAX_FAILURES = "-15 minutes", 5
        failures = db.execute(
            "SELECT COUNT(*) FROM login_attempts "
            "WHERE username = ? AND ip = ? AND attempted_at > datetime('now', ?)",
            (username, request.remote_addr, WINDOW),
        ).fetchone()[0]

        if failures >= MAX_FAILURES:
            return render_template("login.html", error="Too many attempts. Try again later."), 429

        user = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()

        password_hash = user["password_hash"] if user else DUMMY_HASH

        password_verification = check_password_hash(password_hash, password)

        if not user or not password_verification:
            db.execute(
                "INSERT INTO login_attempts (username, ip, attempted_at) "
                "VALUES (?, ?, CURRENT_TIMESTAMP)",
                (username, request.remote_addr)
            )
            db.commit()
            return render_template("login.html", error="Invalid password or username")
        
        db.execute(
            "DELETE FROM login_attempts "
            "WHERE username = ? AND ip = ?",
            (username, request.remote_addr)
        )
        db.commit()

        session.clear()
        session["user_id"] = user["id"]

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("register.html", error="Username is required")

        if len(username) > 64:
            return render_template("register.html", error="Username is too long")

        if not password:
            return render_template("register.html", error="Password is required")
        

        if not confirmation:
            return render_template("register.html", error="Confirmation is required")

        if password != confirmation:
            return render_template("register.html", error="Password did not match")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters")

        MAX_PASSWORD_LENGTH = 128

        if len(password) > MAX_PASSWORD_LENGTH:
            return render_template("register.html", error="Password must 128 character or lesser. ")

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
            MAX_QUANTITY = 100_000
            MAX_RATE = Decimal("1000000")

            quantity = int(quantity)
            if not 1 <= quantity <= MAX_QUANTITY:
                raise ValueError
            
            rate = Decimal(rate_per_unit)
            if not rate.is_finite() or not Decimal("0.01") <= rate <= MAX_RATE:
                raise ValueError

            if rate.as_tuple().exponent < -2:
                raise ValueError

            rate_sen = int(rate * 100)
        except (ArithmeticError, ValueError):
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

    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total_records = db.execute(count_query, params).fetchone()[0]

    page = request.args.get("page", 1, type=int)
    page = max(page, 1)

    per_page = 20

    total_pages = (total_records + per_page - 1) // per_page

    page = min(page, max(total_pages, 1))

    offset = (page - 1) * per_page

    sorts = {
        "newest": " date DESC",
        "oldest": " date ASC",
        "highest": " (quantity * rate_per_unit) DESC",
        "lowest": " (quantity * rate_per_unit) ASC"
    }

    sort = sort if sort in sorts else "newest"

    query += f" ORDER BY {sorts[sort]}, id DESC LIMIT ? OFFSET ?"
    

    records = db.execute(query, params + [per_page, offset]).fetchall()

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

    current_year = date.today().year
    years = list(range(current_year, 2020 - 1, - 1))

    return render_template("records.html", records=records, categories=categories, category=category, months=months ,month=month, search=search, sort=sort, page=page, total_pages=total_pages, total_records=total_records, per_page=per_page, years=years)


@app.route("/records/export")
@login_required
def export():
    month = request.args.get("month", type=int) or None
    year = request.args.get("year")
    keyword = request.args.get("keyword", type=str).strip() or None

    if not year:
        return redirect("/records")

    if len(year) != 4 or not year.isdigit():
        return redirect("/records")

    if month is not None and not 0 < month <= 12:
        return redirect("/records")

    query = "SELECT date, income_type, description, quantity, rate_per_unit FROM income_records WHERE user_id = ? AND strftime('%Y', date) = ?"
    params = [session["user_id"], str(year)]
    
    db = get_db()

    if month:
        query += " AND strftime('%m', date) = ?"
        params.append(f"{month:02d}")

    if keyword:
        query += " AND instr(lower(COALESCE(description, '')), lower(?)) > 0"
        params.append(keyword)
    
    records = db.execute(query, params).fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Category",
        "Description",
        "Quantity",
        "Rate",
        "Total"
    ])

    csv_total = 0

    for record in records:
        rate = record["rate_per_unit"] / 100
        total = record["quantity"] * rate
        csv_total += total

        description = sanitize_csv_value(record["description"])

        writer.writerow([
            record["date"],
            record["income_type"],
            description,
            record["quantity"],
            f"RM{rate:.2f}",
            f"RM{total:.2f}"
        ])

    writer.writerow([
        "",
        "",
        "",
        "",
        "Total Earnings",
        f"RM{csv_total:.2f}",
    ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="salary_tracker.csv"'
        }
    )


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
        return redirect("/records")

    valid_income = ["Teaching", "Freelance", "Event", "Other"]

    # Validate income type
    if income_type not in valid_income:
        return redirect("/records")
    
    # Validate date
    try:
        date.fromisoformat(record_date)
    except ValueError:
        return redirect("/records")

    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        return redirect("/records")

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
        return redirect("/records")

    # Open database
    db = get_db()
    user_id = session["user_id"]

    try:
        db.execute("UPDATE income_records SET date = ?, income_type = ?, description = ?, quantity = ?, rate_per_unit = ? WHERE id = ? AND user_id = ?", (record_date, income_type, description, quantity, rate_per_unit, record_id, user_id))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        print(e)
        return redirect("/records")

    return redirect("/records")



@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")