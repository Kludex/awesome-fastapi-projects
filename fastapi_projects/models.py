from sqlalchemy import Column, DateTime, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from fastapi_projects.database import Base

association_table = Table(
    "association",
    Base.metadata,
    Column("left_id", Integer, ForeignKey("projects.id")),
    Column("right_id", Integer, ForeignKey("dependencies.id")),
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    clone_url = Column(Text, nullable=False, unique=True)
    pushed_at = Column(DateTime, nullable=False)

    dependencies = relationship("Dependency", secondary=association_table)


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
