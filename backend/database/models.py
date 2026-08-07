"""
SQLAlchemy ORM models for the Legal AI System.
All models use SQLAlchemy 2.0 style: Mapped, mapped_column, relationship.
Vectors are stored in ChromaDB only — this file stores metadata only.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

__all__ = ["User", "Lawyer", "Case", "Document", "SessionToken", "SimilarCase"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    """Represents any system user: public visitor, lawyer, or admin."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="public")
    # role values: 'public' | 'lawyer' | 'admin'

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    # Relationships
    lawyer_profile: Mapped["Lawyer | None"] = relationship(
        "Lawyer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    session_tokens: Mapped[list["SessionToken"]] = relationship(
        "SessionToken", back_populates="user", cascade="all, delete-orphan"
    )
    cases: Mapped[list["Case"]] = relationship(
        "Case", foreign_keys="Case.created_by_user_id", back_populates="created_by"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="uploaded_by"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


# ---------------------------------------------------------------------------
# Lawyer
# ---------------------------------------------------------------------------

class Lawyer(Base):
    """Extended profile for users with role='lawyer'."""

    __tablename__ = "lawyers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bar_council_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    firm_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON columns for list data (PostgreSQL JSONB would also work)
    specializations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    court_types: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    languages: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["English"], nullable=False)
    previous_cases: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cases_handled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lawyer_profile")
    cases: Mapped[list["Case"]] = relationship(
        "Case", foreign_keys="Case.lawyer_id", back_populates="lawyer"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", secondary="users",
        primaryjoin="Lawyer.user_id == User.id",
        secondaryjoin="User.id == Document.uploaded_by_user_id",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<Lawyer id={self.id} name={self.name}>"


# ---------------------------------------------------------------------------
# Case
# ---------------------------------------------------------------------------

class Case(Base):
    """A legal case or matter managed by a lawyer."""

    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lawyer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    case_type: Mapped[str] = mapped_column(String(100), nullable=False)
    legal_domain: Mapped[str] = mapped_column(String(100), nullable=False, default="General")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    # status values: active | pending | closed | archived

    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    court_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    court_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    judge_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    next_hearing: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    facts: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON columns (store lists/dicts)
    issues: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parties: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    ipc_sections: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    precedents: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    ai_insights: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    tasks: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    timeline: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    document_checklist: Mapped[dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    # Relationships
    lawyer: Mapped["Lawyer | None"] = relationship("Lawyer", back_populates="cases")
    created_by: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by_user_id], back_populates="cases"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="case", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Case id={self.id} title={self.title!r} status={self.status}>"


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(Base):
    """
    Metadata for uploaded legal documents.
    The actual vectors are stored in ChromaDB under collection_name.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    collection_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # collection_name is the ChromaDB collection where this doc's chunks are stored

    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True
    )

    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)  # bytes
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    # Relationships
    uploaded_by: Mapped["User"] = relationship("User", back_populates="documents")
    case: Mapped["Case | None"] = relationship("Case", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document id={self.id} file_name={self.file_name!r}>"


# ---------------------------------------------------------------------------
# SessionToken
# ---------------------------------------------------------------------------

class SessionToken(Base):
    """Secure session token for authenticated users (24-hour lifetime)."""

    __tablename__ = "session_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="session_tokens")

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<SessionToken user_id={self.user_id} expires_at={self.expires_at}>"


# ---------------------------------------------------------------------------
# SimilarCase
# ---------------------------------------------------------------------------

class SimilarCase(Base):
    """
    Metadata for similar/precedent cases.
    Vectors (embeddings) are stored ONLY in ChromaDB under the 'similar_cases' collection.
    This table stores searchable metadata only — never embeddings.
    """

    __tablename__ = "similar_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    court_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    citation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    legal_domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="local_index")
    # source values: local_index | bharat_courts_archive | manual

    # The ChromaDB document ID that links this row to its embedding
    chroma_doc_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    ipc_sections: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parties: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )

    def __repr__(self) -> str:
        return f"<SimilarCase id={self.id} case_name={self.case_name!r}>"

