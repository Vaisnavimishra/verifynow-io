import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Portable JSON column: real JSONB on Postgres (production), plain JSON
# elsewhere (e.g. SQLite in tests) -- so the same models work against both
# without any behavior difference that matters for this app.
PortableJSON = JSON().with_variant(JSONB(), "postgresql")

# UUIDs stored as 36-char strings so the schema is portable across Postgres
# (production) and SQLite (tests) without dialect-specific column types.
UUIDStr = String(36)


class Base(DeclarativeBase):
    pass


class ContentType(str, enum.Enum):
    TEXT = "text"
    URL = "url"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO_URL = "video_url"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Verdict(str, enum.Enum):
    VERIFIED = "VERIFIED"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNCERTAIN = "UNCERTAIN"


class EvidenceStance(str, enum.Enum):
    SUPPORTS = "supports"
    REFUTES = "refutes"
    CONTEXT = "context"


def _uuid() -> str:
    return str(uuid.uuid4())


class AnalysisRequest(Base):
    """One user submission and its verification outcome."""

    __tablename__ = "analysis_requests"

    id: Mapped[str] = mapped_column(UUIDStr, primary_key=True, default=_uuid)

    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType, name="content_type"))
    # Raw user-facing summary of what was submitted (text snippet, URL, or filename).
    input_summary: Mapped[str] = mapped_column(Text)
    # Hash of normalized content, used for cache lookups / de-duplication.
    normalized_hash: Mapped[str] = mapped_column(String(64), index=True)

    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status"), default=RequestStatus.PENDING
    )

    verdict: Mapped[Verdict | None] = mapped_column(Enum(Verdict, name="verdict"), nullable=True)
    # Confidence is only ever populated when the verification service explicitly
    # returned one backed by retrieved evidence. NULL means "not stated" -- never
    # a fabricated placeholder number.
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # When the content itself claims to have been published/created, if determinable.
    content_published_date: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # For URL/website submissions: domain, site_name, about, founding_date, founder,
    # company_info, claims[] and per-claim verification status. Structured as JSON
    # because its shape is genuinely variable (a lot of these fields are legitimately
    # "unknown" and are represented as null rather than omitted or guessed).
    website_metadata: Mapped[dict | None] = mapped_column(PortableJSON, nullable=True)

    # AI-generated-content signal, kept explicitly separate from the factual verdict.
    ai_generated_signal: Mapped[dict | None] = mapped_column(PortableJSON, nullable=True)

    # Server-extracted text actually used as verification input: parsed document
    # text, fetched page text, or the caption/claim extracted from an image.
    # Never a placeholder -- absent extraction means this stays NULL and the
    # request is marked failed/uncertain instead.
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    from_cache: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    sources: Mapped[list["EvidenceSource"]] = relationship(
        back_populates="analysis_request", cascade="all, delete-orphan"
    )


class EvidenceSource(Base):
    """A single retrieved source backing (or refuting) part of a verdict."""

    __tablename__ = "evidence_sources"

    id: Mapped[str] = mapped_column(UUIDStr, primary_key=True, default=_uuid)
    analysis_request_id: Mapped[str] = mapped_column(
        UUIDStr, ForeignKey("analysis_requests.id", ondelete="CASCADE")
    )

    claim: Mapped[str] = mapped_column(Text)
    stance: Mapped[EvidenceStance] = mapped_column(Enum(EvidenceStance, name="evidence_stance"))
    source_name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(Text)
    # Publication date of the SOURCE (not the submitted content), if known.
    published_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis_request: Mapped["AnalysisRequest"] = relationship(back_populates="sources")
