from validators import validate_salary_data
import sys

print(sys.path)

def test_valid_salary_data():
    data = {
        "income_type": "Teaching",
        "date": "2026-11-19",
        "quantity": "3",
        "rate_per_unit": "25.00",
        "description": "Weekend coaching"
    }

    result, error = validate_salary_data(data)

    assert error is None
    assert result["income_type"] == "Teaching"
    assert result["quantity"] == 3
    assert result["rate_per_unit"] == 2500
    assert result["description"] == "Weekend coaching"

def test_invalid_income_type():
    data = {
        "income_type": "Gaming",
        "date": "2026-11-19",
        "quantity": "3",
        "rate_per_unit": "25.00",
        "description": ""
    }

    result, error = validate_salary_data(data)

    assert result is None
    assert error == "Invalid income type. "