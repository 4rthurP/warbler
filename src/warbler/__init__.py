import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import create_engine

from .models import Base

load_dotenv()

sqlite_path = os.getenv("WARBLER_SQLITE_PATH")
if sqlite_path:
    engine = create_engine(f"sqlite:///{sqlite_path}/warbler.sqlite")
else:
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('WARBLER_DATABASE_USER')}:{os.getenv('WARBLER_DATABASE_PASSWORD')}@{os.getenv('WARBLER_DATABASE_HOST')}:{os.getenv('WARBLER_DATABASE_PORT')}/{os.getenv('WARBLER_DATABASE_NAME')}"
    )

LOCAL_TZ = ZoneInfo(os.getenv("LOCAL_TZ", "Europe/Paris"))

APP_ROOT = Path(__file__).resolve().parent
LOCK_FILE = APP_ROOT / "initialized.lock"


def initialize_database():
    if LOCK_FILE.exists():
        return

    # Create all tables from SQLAlchemy models
    Base.metadata.create_all(engine)

    with LOCK_FILE.open("w") as f:
        f.write("initialized")


initialize_database()
