from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite://database.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SessionManager:
    def __enter__(self):
        self.session = SessionLocal()
        return self.session

    def __exit__(self, *exc_data):
        self.session.close()
