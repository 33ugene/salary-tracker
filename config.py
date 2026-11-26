import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured. ")

APP_ENV = os.environ.get("APP_ENV")

if not APP_ENV:
    raise RuntimeError("APP_ENV not configured. ")

if APP_ENV not in ("development", "production"):
    raise RuntimeError(f"Invalid APP_ENV: {APP_ENV}. "
                        "Expected 'development' or 'production'. "
    )

IS_PRODUCTION = APP_ENV == "production"

DATABASE = (
    os.environ.get("DATABASE", "/data/salary.db")
    if IS_PRODUCTION
    else "database/salary_dev.db"
)