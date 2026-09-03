from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ContentTypeEnum(str, Enum):
    text = "text"
    url = "url"
    document = "document"
    image = "image"
    video_url = "video_url"


class VerdictEnum(str, Enum):
    VERIFIED = "VERIFIED"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNCERTAIN = "UNCERTAIN"


class EvidenceStanceEnum(str, Enum):
    supports = "supports"
    refutes = "refutes"
    context = "context"


# ---------------------------------------------------------------------------
# What we ask the LLM verification layer to return. This is the ONLY place
# a verdict/confidence/evidence is allowed to originate from -- never
# generated locally without grounding.
# ---------------------------------------------------------------------------


class EvidenceItem(BaseModel):
    claim: str
    stance: EvidenceStanceEnum
    source_name: str
    source_url: str
    published_date: str | None = None
    excerpt: str | None = Field(
        default=None,
        description="Short paraphrase (not a verbatim quote) of what the source says.",
    )


class WebsiteMetadata(BaseModel):
    domain: str | None = None
    site_name: str | None = None
    about: str | None = None
    founding_or_launch_date: str | None = None
    founder_or_organization: str | None = None
    company_info: str | None = None
    claims_made_by_site: list[str] = Field(default_factory=list)
    independently_verified_claims: list[str] = Field(
        default_factory=list,
        description="Subset of claims_made_by_site that an independent source corroborated.",
    )


class AIGeneratedSignal(BaseModel):
    """Explicitly separate from the factual verdict. Never used to justify FALSE/VERIFIED."""

    likely_ai_generated: bool | None = None
    note: str | None = None


class VerificationOutcome(BaseModel):
    """Structured result the verification service must produce."""

    verdict: VerdictEnum
    confidence: int | None = Field(
        default=None, ge=0, le=100, description="Only set when justified by retrieved evidence."
    )
    reasoning: str
    content_published_date: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    website_metadata: WebsiteMetadata | None = None
    ai_generated_signal: AIGeneratedSignal | None = None
    limitations: str


# ---------------------------------------------------------------------------
# API request/response schemas
# ---------------------------------------------------------------------------


class VerifyRequestStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class VerifySubmitResponse(BaseModel):
    request_id: str
    status: VerifyRequestStatus
    from_cache: bool = False


class EvidenceItemOut(BaseModel):
    claim: str
    stance: EvidenceStanceEnum
    source_name: str
    source_url: str
    published_date: str | None = None
    excerpt: str | None = None

    model_config = {"from_attributes": True}


class VerificationResultOut(BaseModel):
    request_id: str
    content_type: ContentTypeEnum
    status: VerifyRequestStatus
    input_summary: str
    verdict: VerdictEnum | None = None
    confidence: int | None = None
    reasoning: str | None = None
    content_published_date: str | None = None
    website_metadata: WebsiteMetadata | None = None
    ai_generated_signal: AIGeneratedSignal | None = None
    evidence: list[EvidenceItemOut] = Field(default_factory=list)
    limitations: str | None = None
    error_message: str | None = None
    from_cache: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HistoryItemOut(BaseModel):
    request_id: str
    content_type: ContentTypeEnum
    status: VerifyRequestStatus
    input_summary: str
    verdict: VerdictEnum | None = None
    confidence: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
