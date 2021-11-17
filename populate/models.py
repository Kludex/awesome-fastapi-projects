import tempfile
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar

import humps
from git import Repo
from sqlalchemy import Column, inspect
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

Self = TypeVar("Self", bound="Base")


@as_declarative()
class Base:
    __name__: str

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @declared_attr
    def __tablename__(cls) -> str:
        return humps.depascalize(cls.__name__)

    def dict(self) -> Dict[str, Any]:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @classmethod
    def get(cls, session: Session, *args: Any, **kwargs: Any) -> Optional[Self]:
        return session.query(cls).filter(*args).filter_by(**kwargs).first()


class Repository(Base):
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    clone_url = Column(String, nullable=False)
    stargazers = Column(Integer, nullable=False)

    packages = relationship("Package", secondary="dependency")

    def clone(self, repo_dir: tempfile.TemporaryDirectory) -> Repo:
        return Repo.clone_from(self.clone_url, repo_dir, depth=1)


class Package(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    repositories = relationship("Repository", secondary="dependency")


class Dependency(Base):
    repository_id = Column(Integer, ForeignKey("repository.id"), primary_key=True)
    package_id = Column(Integer, ForeignKey("package.id"), primary_key=True)
