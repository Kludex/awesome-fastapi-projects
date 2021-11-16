import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_dir = os.path.abspath(os.getcwd() + "/data/db.sqlite")
engine = create_engine("sqlite:///" + db_dir, connect_args={"check_same_thread": True})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
