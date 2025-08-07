import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import create_engine

from .models import Base

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('WARBLER_DATABASE_USER')}:{os.getenv('WARBLER_DATABASE_PASSWORD')}@{os.getenv('WARBLER_DATABASE_HOST')}:{os.getenv('WARBLER_DATABASE_PORT')}/{os.getenv('WARBLER_DATABASE_NAME')}"
)

LOCAL_TZ = ZoneInfo(os.getenv("LOCAL_TZ", "Europe/Paris"))

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(APP_ROOT, "initialized.lock")


def initialize_database():
    if os.path.exists(LOCK_FILE):
        return

    # Create all tables from SQLAlchemy models
    Base.metadata.create_all(engine)

    with open(LOCK_FILE, "w") as f:
        f.write("initialized")


initialize_database()
