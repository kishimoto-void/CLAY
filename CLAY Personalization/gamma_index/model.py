"""Data contracts for Gamma Index. Standard library only; no network or persistence."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class EntryStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class HoldReason(str, Enum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_CANDIDATES = "CONFLICTING_CANDIDATES"
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    MISSING_CAPABILITY = "MISSING_CAPABILITY"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    POLICY_REVIEW = "POLICY_REVIEW"
    VERSION_COLLISION = "VERSION_COLLISION"
    OTHER = "OTHER"


class HoldStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class GammaEntry:
    entry_id: str
    resource_id: str
    version: str
    resource_kind: str
    scope: str
    content_digest: str
    source_ref: str
    source_status: str = "UNVERIFIED"
    status: EntryStatus = EntryStatus.CANDIDATE
    claims: Tuple[str, ...] = field(default_factory=tuple)
    tags: Tuple[str, ...] = field(default_factory=tuple)
    created_at: Optional[str] = None


@dataclass(frozen=True)
class HoldRecord:
    hold_id: str
    entry_id: str
    reason: HoldReason
    open_questions: Tuple[str, ...]
    preserved_refs: Tuple[str, ...] = field(default_factory=tuple)
    opened_at: Optional[str] = None
    revisit_trigger: Optional[str] = None
    status: HoldStatus = HoldStatus.OPEN
    resolution: Optional[str] = None
    resolution_evidence_ref: Optional[str] = None
    closed_at: Optional[str] = None


@dataclass(frozen=True)
class GammaSearchResult:
    entry: GammaEntry
    open_holds: Tuple[HoldRecord, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GammaDiscoveryPage:
    """Deterministic metadata-only search page; not an authorization decision."""
    query: str
    scope: Optional[str]
    offset: int
    limit: int
    revision: int
    matched_count: int
    results: Tuple[GammaSearchResult, ...]
    next_offset: Optional[int]

    @property
    def truncated(self) -> bool:
        return self.next_offset is not None


@dataclass(frozen=True)
class GammaHandoff:
    """Reference-only handoff. It never grants retrieval or activation authority."""
    entry_id: str
    resource_id: str
    version: str
    resource_kind: str
    scope: str
    content_digest: str
    source_ref: str
    source_status: str
    index_status: str
    required_host_checks: Tuple[str, ...] = (
        "SOURCE_AUTHENTICATION",
        "PERMISSION_CHECK",
        "CAPABILITY_CHECK",
        "COMPATIBILITY_CHECK",
        "SAFETY_POLICY_CHECK",
        "APPROVAL_IF_REQUIRED",
    )
    retrieval_authorized: bool = False
    activation_authorized: bool = False
