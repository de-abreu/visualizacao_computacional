# pyright: reportAny=false

from sqlalchemy import PrimaryKeyConstraint as pkc, ForeignKey as fk
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column as column,
    relationship,
)
from typing import final

Base = declarative_base()


@final
class Researcher(Base):
    __tablename__ = "researchers"

    # Attributes
    lattes_id: Mapped[str] = column(primary_key=True)
    name: Mapped[str]

    # Relationships
    articles: Mapped[list["Article"]] = relationship(
        secondary="authorship", back_populates="authors"
    )
    projects: Mapped[list["Project"]] = relationship(
        secondary="participation", back_populates="participants"
    )


@final
class Authorship(Base):
    __tablename__ = "authorship"

    author_id: Mapped[str] = column(fk("researchers.lattes_id", ondelete="CASCADE"))
    article_id: Mapped[int] = column(fk("articles.id", ondelete="CASCADE"))

    __table_args__ = (pkc("author_id", "article_id"),)


@final
class Article(Base):
    __tablename__ = "articles"

    # Attributes
    id: Mapped[int] = column(primary_key=True, autoincrement=True)
    title: Mapped[str] = column(unique=True)
    year: Mapped[int]

    # Relationships
    authors: Mapped[list["Researcher"]] = relationship(
        secondary="authorship", back_populates="articles"
    )


@final
class Participation(Base):
    __tablename__ = "participation"

    # Attributes
    participant_id: Mapped[str] = column(
        fk("researchers.lattes_id", ondelete="CASCADE")
    )
    project_id: Mapped[int] = column(fk("projects.id", ondelete="CASCADE"))
    role: Mapped[str] = column(default="Integrante")

    __table_args__ = (pkc("participant_id", "project_id"),)


@final
class Project(Base):
    __tablename__ = "projects"

    # Attributes
    id: Mapped[int] = column(primary_key=True, autoincrement=True)
    name: Mapped[str] = column(unique=True)
    start: Mapped[int]
    end: Mapped[int | None] = column(default=None)
    type: Mapped[str | None] = column(default=None)

    # Relationships
    participants: Mapped[list["Researcher"]] = relationship(
        secondary="participation", back_populates="projects"
    )
