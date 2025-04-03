import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import timezone

load_dotenv()

engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

local_tz = timezone(os.getenv('LOCAL_TZ'))

app_root = os.path.dirname(os.path.abspath(__file__))