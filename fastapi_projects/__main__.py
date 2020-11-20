import logging
import os
import re
import shutil
from contextlib import contextmanager
from typing import Set

from git import Git
from git.exc import GitCommandError
from github import Github
from github.Repository import Repository
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer, String

logging.basicConfig(level=logging.INFO)

# Github
github_access_token = os.getenv("ACCESS_TOKEN_GITHUB")
g = Github(github_access_token)

MAX_SIZE = 100 * 1000  # 100 MB

# Directory
dir = os.getcwd()
clone_dir = os.path.join(dir, "tmp")

INVALID_FOLDERS = ("site-packages", "venv")

# Database
engine = create_engine("sqlite:///packages.db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Association(Base):
    __tablename__ = "association"

    package_id = Column(Integer, ForeignKey("package.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)

    package = relationship("Package", backref="package_associations")
    project = relationship("Project", backref="project_associations")


class Package(Base):
    __tablename__ = "package"
    __table_args__ = (UniqueConstraint("name"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Project(Base):
    __tablename__ = "project"
    __table_args__ = (UniqueConstraint("name", "owner"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String)
    packages = relationship("Package", secondary="association")


Base.metadata.create_all(engine, checkfirst=True)


@contextmanager
def get_session():
    session = SessionLocal()
    yield session
    session.close()


# Functions
def clone(repository: Repository):
    try:
        clone_url = repository.clone_url
        Git(clone_dir).clone(clone_url)
    except GitCommandError:
        pass


def get_packages_from_file(path: str) -> Set[str]:
    packages = set()
    logging.info("Reading file '%s'.", path)
    try:
        with open(path, "r") as file:
            for line in file.readlines():
                result = re.search(r"from (\w+)[\.\w+]*|:[ ]*import (\w*)\n", line)
                if result:
                    if result.group(1):
                        packages.add(result.group(1))
                    if result.group(2):
                        packages.add(result.group(2))
    except FileNotFoundError:
        logging.info("File not found '%s'.", path)
    except UnicodeDecodeError:
        logging.info("Invalid character on file '%s'.", path)
    return packages


def extract_data(repository: Repository) -> dict:
    data = {}
    for (root, _, files) in os.walk(os.path.join(clone_dir, repository.name)):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".py") and all(
                folder not in path for folder in INVALID_FOLDERS
            ):
                data["packages"] = get_packages_from_file(path)
    return data


def run():
    snippets = g.search_code('l=Python&q="from+fastapi+import+FastAPI"&type=Code')
    for snippet in snippets:
        repository = snippet.repository
        name = repository.name
        owner = repository.owner.name
        logging.info("Got repository '%s'.", name)

        with get_session() as session:
            if (
                session.query(Project)
                .filter(Project.name == name, Project.owner == owner)
                .first()
            ):
                continue

        # NOTE: When deployed! Ignore repositories that didn't change.
        # from datetime import datetime
        # commits = repository.get_commits()
        # last_commit_date = [commit.commit.author.date for commit in commits][0]
        # if (datetime.today() - last_commit_date).days > 7:
        #     continue

        if repository.size > MAX_SIZE:
            continue

        logging.info("Cloning repository '%s'.", name)
        clone(repository)

        logging.info("Extracting data from '%s'.", name)
        data = extract_data(repository)

        with get_session() as session:
            project = Project(name=name, owner=owner)
            for package_name in data.get("packages", {}):
                package = (
                    session.query(Package).filter(Package.name == package_name).first()
                )
                if package is None:
                    package = Package(name=package_name)
                project.packages.append(package)
            session.add(project)
            session.commit()

        logging.info("Removing repository '%s'.", name)
        shutil.rmtree(os.path.join(clone_dir, name))


# Run!
run()
