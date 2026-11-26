from decimal import Decimal, InvalidOperation
from datetime import date

def validate_income_type(income_type: str):
    valid_income = ["Teaching", "Freelance", "Event", "Other"]

    return income_type in valid_income


def validate_date(record_date: str):
    try:
        date.fromisoformat(record_date)
        if not isinstance(record_date, str) or len(record_date) != 10:
            raise ValueError
    except (ValueError, TypeError):
        return None
    return True


def validate_quantity(quantity):
    MAX_QUANTITY = 100_000
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return None

    if not 0 < quantity <= MAX_QUANTITY:
        return None
    return quantity

def validate_rate(rate):
    MAX_RATE = Decimal("1000000")
    try:
        rate = Decimal(rate)
    except (InvalidOperation, TypeError):
        return None

    if not rate.is_finite() or not Decimal("0.01") <= rate <= MAX_RATE:
        return None

    if rate.as_tuple().exponent < -2:
        return None
    rate_sen = int(rate * 100)
    return rate_sen

def validate_salary_data(form_data):
    income_type = form_data.get("income_type", "").strip()
    record_date = form_data.get("date", "").strip()
    quantity = form_data.get("quantity", "").strip()
    rate = form_data.get("rate_per_unit", "").strip()
    description = form_data.get("description", "").strip() or None

    if not validate_income_type(income_type):
        return None, "Invalid income type. "

    if not validate_date(record_date):
        return None, "Invalid date format"
    
    quantity = validate_quantity(quantity)

    if quantity is None:
        return None, "Invalid quantity"
    
    rate = validate_rate(rate)

    if rate is None:
        return None, "Invalid rate"

    if description is not None:
        if len(description) > 250:
            return None, "Description is too long."

    return {
        "income_type": income_type,
        "date": record_date,
        "quantity": quantity,
        "rate_per_unit": rate,
        "description": description
    }, None

