import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

from .models import Base

load_dotenv()

engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

LOCAL_TZ = ZoneInfo(os.getenv("LOCAL_TZ", "Europe/Paris"))

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

LOCK_FILE = os.path.join(APP_ROOT, "initialized.lock")

CRON_LOG_FILE = os.getenv("CRON_LOG_FILE", "/var/log/cron.log")

def initialize_database():
    if os.path.exists(LOCK_FILE):
        return

    # Create all tables from SQLAlchemy models
    Base.metadata.create_all(engine)

    with open(LOCK_FILE, "w") as f:
        f.write("initialized")

initialize_database()