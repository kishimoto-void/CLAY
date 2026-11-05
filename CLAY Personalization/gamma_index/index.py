"""In-memory Gamma Index with explicit discover -> resolve -> handoff phases.

Gamma is a metadata index. It does not fetch payloads, authenticate sources,
make permission decisions, authorize actions, or activate resources.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from itertools import islice
import re
from threading import RLock
from typing import Iterable, Optional

from .model import (
    EntryStatus, GammaDiscoveryPage, GammaEntry, GammaHandoff,
    GammaSearchResult, HoldReason, HoldRecord, HoldStatus,
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MAX_ENTRIES = 10_000
_MAX_HOLDS = 50_000
_MAX_QUERY_LENGTH = 512
_MAX_TAGS = 32
_MAX_TAG_LENGTH = 64
_MAX_PAGE_SIZE = 100
_MAX_OFFSET = 10_000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GammaIndexError(ValueError):
    pass


class GammaIndex:
    """Metadata registry with three explicit phases.

    1. discover(): bounded, deterministic candidate discovery.
    2. resolve(): exact-ID and expected-identity checks; no implicit winner.
    3. handoff(): reference-only envelope for separate host validation.

    Legacy search()/get() remain available for compatibility.
    """

    def __init__(self) -> None:
        self._entries: dict[str, GammaEntry] = {}
        self._holds: dict[str, HoldRecord] = {}
        self._revision = 0
        self._lock = RLock()

    def register(self, entry: GammaEntry) -> GammaEntry:
        # Normalize once, before indexing. This freezes caller-owned lists and avoids
        # consuming one-shot iterables twice during validation/registration.
        entry = self._validate_entry(entry)
        with self._lock:
            existing = self._entries.get(entry.entry_id)
            if existing is not None:
                # Auto-generated created_at must not make an exact replay look different.
                if replace(existing, created_at=None) == replace(entry, created_at=None):
                    return existing
                raise GammaIndexError("ENTRY_ID_COLLISION: immutable entry_id already exists")
            if entry.status is not EntryStatus.CANDIDATE:
                raise GammaIndexError("INITIAL_STATUS_MUST_BE_CANDIDATE")
            if len(self._entries) >= _MAX_ENTRIES:
                raise GammaIndexError("ENTRY_LIMIT_EXCEEDED")
            if any(e.resource_id == entry.resource_id and e.version == entry.version
                   and e.content_digest != entry.content_digest for e in self._entries.values()):
                raise GammaIndexError("VERSION_COLLISION: same resource/version has a different digest")
            stored = entry if entry.created_at else replace(entry, created_at=_now())
            self._entries[stored.entry_id] = stored
            self._revision += 1
            return stored

    def hold(
        self,
        entry_id: str,
        hold_id: str,
        reason: HoldReason,
        open_questions: Iterable[str],
        preserved_refs: Iterable[str] = (),
        revisit_trigger: Optional[str] = None,
    ) -> HoldRecord:
        if not isinstance(hold_id, str) or not _ID_RE.fullmatch(hold_id):
            raise GammaIndexError("INVALID_HOLD_ID")
        questions = self._normalize_text_items(
            open_questions, error="HOLD_REQUIRES_QUESTION_LIST", max_items=64, max_length=2000
        )
        if not questions:
            raise GammaIndexError("HOLD_REQUIRES_OPEN_QUESTION")
        refs = self._normalize_text_items(
            preserved_refs, error="PRESERVED_REFS_MUST_BE_LIST", max_items=256, max_length=2048
        )
        if not isinstance(reason, HoldReason):
            raise GammaIndexError("INVALID_HOLD_REASON")
        if revisit_trigger is not None and (not isinstance(revisit_trigger, str)
                                             or not revisit_trigger.strip()
                                             or len(revisit_trigger) > 2000):
            raise GammaIndexError("INVALID_REVISIT_TRIGGER")
        with self._lock:
            entry = self._entries.get(entry_id)
            if entry is None:
                raise GammaIndexError("ENTRY_NOT_FOUND")
            if hold_id in self._holds:
                raise GammaIndexError("HOLD_ID_COLLISION")
            if len(self._holds) >= _MAX_HOLDS:
                raise GammaIndexError("HOLD_LIMIT_EXCEEDED")
            if entry.status in (EntryStatus.REJECTED, EntryStatus.SUPERSEDED):
                raise GammaIndexError("TERMINAL_ENTRY_CANNOT_BE_HELD")
            record = HoldRecord(
                hold_id=hold_id,
                entry_id=entry_id,
                reason=reason,
                open_questions=questions,
                preserved_refs=refs,
                opened_at=_now(),
                revisit_trigger=revisit_trigger,
            )
            self._holds[hold_id] = record
            self._entries[entry_id] = replace(entry, status=EntryStatus.HELD)
            self._revision += 1
            return record

    def close_hold(self, hold_id: str, outcome: EntryStatus, resolution: str,
                   evidence_ref: str) -> HoldRecord:
        if outcome not in (EntryStatus.AVAILABLE, EntryStatus.RESOLVED,
                           EntryStatus.REJECTED, EntryStatus.SUPERSEDED):
            raise GammaIndexError("INVALID_HOLD_OUTCOME")
        if (not isinstance(resolution, str) or not resolution.strip() or len(resolution) > 2000
                or not isinstance(evidence_ref, str) or not evidence_ref.strip()
                or len(evidence_ref) > 2048):
            raise GammaIndexError("HOLD_RESOLUTION_REQUIRES_EVIDENCE_AND_RATIONALE")
        with self._lock:
            hold = self._holds.get(hold_id)
            if hold is None:
                raise GammaIndexError("HOLD_NOT_FOUND")
            if hold.status is HoldStatus.CLOSED:
                raise GammaIndexError("HOLD_ALREADY_CLOSED")
            entry = self._entries[hold.entry_id]
            closed = replace(hold, status=HoldStatus.CLOSED, resolution=resolution.strip(),
                             resolution_evidence_ref=evidence_ref.strip(), closed_at=_now())
            self._holds[hold_id] = closed
            other_open_holds = [h for h in self._holds.values()
                                if h.entry_id == entry.entry_id
                                and h.hold_id != hold_id and h.status is HoldStatus.OPEN]
            resulting_status = EntryStatus.HELD if other_open_holds else outcome
            self._entries[entry.entry_id] = replace(entry, status=resulting_status)
            self._revision += 1
            return closed

    def discover(self, query: str = "", tags: Iterable[str] = (), *,
                 scope: Optional[str] = None, limit: int = 50,
                 offset: int = 0, include_held: bool = False,
                 expected_revision: Optional[int] = None) -> GammaDiscoveryPage:
        """Phase G1: discover metadata candidates; held entries are excluded by default.

        Pass the previous page's revision as expected_revision on continuation. A changed
        index fails closed instead of silently shifting offset-based pages.
        """
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= _MAX_PAGE_SIZE:
            raise GammaIndexError("INVALID_DISCOVERY_LIMIT")
        if not isinstance(offset, int) or isinstance(offset, bool) or not 0 <= offset <= _MAX_OFFSET:
            raise GammaIndexError("INVALID_DISCOVERY_OFFSET")
        if scope is not None and (not isinstance(scope, str) or not scope.strip() or len(scope) > 128):
            raise GammaIndexError("INVALID_SCOPE_FILTER")
        if not isinstance(include_held, bool):
            raise GammaIndexError("INVALID_INCLUDE_HELD")
        if expected_revision is not None and (
            not isinstance(expected_revision, int) or isinstance(expected_revision, bool)
            or expected_revision < 0
        ):
            raise GammaIndexError("INVALID_EXPECTED_REVISION")
        if offset > 0 and expected_revision is None:
            raise GammaIndexError("DISCOVERY_CONTINUATION_REQUIRES_REVISION")
        with self._lock:
            if expected_revision is not None and expected_revision != self._revision:
                raise GammaIndexError("STALE_DISCOVERY_PAGE_RESTART_REQUIRED")
            revision = self._revision
            all_results = self.search(query=query, tags=tags, include_held=include_held, scope=scope)
            page = all_results[offset:offset + limit]
            next_offset = offset + len(page) if offset + len(page) < len(all_results) else None
            return GammaDiscoveryPage(
                query=query.strip(), scope=scope, offset=offset, limit=limit,
                revision=revision, matched_count=len(all_results), results=page,
                next_offset=next_offset,
            )

    def resolve(self, entry_id: str, *, expected_resource_id: Optional[str] = None,
                expected_version: Optional[str] = None,
                expected_digest: Optional[str] = None,
                expected_scope: Optional[str] = None) -> GammaSearchResult:
        """Phase G2: resolve one exact candidate; never infer a winner from ranking."""
        if not isinstance(entry_id, str) or not _ID_RE.fullmatch(entry_id):
            raise GammaIndexError("INVALID_ENTRY_ID")
        with self._lock:
            result = self.get(entry_id)
            if result is None:
                raise GammaIndexError("ENTRY_NOT_FOUND")
            entry = result.entry
            if entry.status is EntryStatus.HELD or result.open_holds:
                raise GammaIndexError("ENTRY_HELD_REQUIRES_EXPLICIT_RESOLUTION")
            if entry.status in (EntryStatus.REJECTED, EntryStatus.SUPERSEDED):
                raise GammaIndexError("ENTRY_NOT_ELIGIBLE_FOR_HANDOFF")
            expected = {
                "resource_id": (expected_resource_id, 256),
                "version": (expected_version, 64),
                "content_digest": (expected_digest, 64),
                "scope": (expected_scope, 128),
            }
            for field_name, (expected_value, max_length) in expected.items():
                if expected_value is not None:
                    if (not isinstance(expected_value, str) or not expected_value.strip()
                            or len(expected_value) > max_length):
                        raise GammaIndexError(f"INVALID_EXPECTED_{field_name.upper()}")
                    if field_name == "content_digest" and not _DIGEST_RE.fullmatch(expected_value):
                        raise GammaIndexError("INVALID_EXPECTED_CONTENT_DIGEST")
                    if getattr(entry, field_name) != expected_value:
                        raise GammaIndexError(f"IDENTITY_MISMATCH_{field_name.upper()}")
            return result

    def handoff(self, entry_id: str, *, expected_resource_id: Optional[str] = None,
                expected_version: Optional[str] = None,
                expected_digest: Optional[str] = None,
                expected_scope: Optional[str] = None) -> GammaHandoff:
        """Phase G3: return a reference-only envelope; host must perform all checks."""
        result = self.resolve(
            entry_id, expected_resource_id=expected_resource_id,
            expected_version=expected_version, expected_digest=expected_digest,
            expected_scope=expected_scope,
        )
        entry = result.entry
        if entry.source_status == "FAILED":
            raise GammaIndexError("SOURCE_STATUS_FAILED")
        return GammaHandoff(
            entry_id=entry.entry_id,
            resource_id=entry.resource_id,
            version=entry.version,
            resource_kind=entry.resource_kind,
            scope=entry.scope,
            content_digest=entry.content_digest,
            source_ref=entry.source_ref,
            source_status=entry.source_status,
            index_status=entry.status.value,
        )

    def get(self, entry_id: str) -> Optional[GammaSearchResult]:
        with self._lock:
            entry = self._entries.get(entry_id)
            if entry is None:
                return None
            holds = tuple(h for h in self._holds.values()
                          if h.entry_id == entry_id and h.status is HoldStatus.OPEN)
            return GammaSearchResult(entry, holds)

    def search(self, query: str = "", tags: Iterable[str] = (),
               include_held: bool = True, scope: Optional[str] = None
               ) -> tuple[GammaSearchResult, ...]:
        if not isinstance(query, str) or len(query) > _MAX_QUERY_LENGTH:
            raise GammaIndexError("INVALID_QUERY")
        normalized_tags = self._normalize_text_items(
            tags, error="TAGS_MUST_BE_LIST", max_items=_MAX_TAGS,
            max_length=_MAX_TAG_LENGTH, allow_empty=False,
        )
        if not isinstance(include_held, bool):
            raise GammaIndexError("INVALID_INCLUDE_HELD")
        if scope is not None and (not isinstance(scope, str) or not scope.strip() or len(scope) > 128):
            raise GammaIndexError("INVALID_SCOPE_FILTER")
        q = query.casefold().strip()
        wanted = {t.casefold() for t in normalized_tags}
        with self._lock:
            results: list[GammaSearchResult] = []
            for entry in self._entries.values():
                if entry.status in (EntryStatus.REJECTED, EntryStatus.SUPERSEDED):
                    continue
                if entry.status is EntryStatus.HELD and not include_held:
                    continue
                if scope is not None and entry.scope != scope:
                    continue
                haystack = " ".join((entry.entry_id, entry.resource_id, entry.resource_kind,
                                     entry.scope, *entry.claims, *entry.tags)).casefold()
                if q and q not in haystack:
                    continue
                entry_tags = {t.casefold() for t in entry.tags}
                if wanted and not wanted.issubset(entry_tags):
                    continue
                holds = tuple(h for h in self._holds.values()
                              if h.entry_id == entry.entry_id and h.status is HoldStatus.OPEN)
                results.append(GammaSearchResult(entry, holds))
            # Stable ordering avoids relying on registration/insertion order. It is not relevance ranking.
            results.sort(key=lambda result: (
                result.entry.resource_id.casefold(), result.entry.version,
                result.entry.entry_id.casefold(),
            ))
            return tuple(results)

    def snapshot(self) -> dict:
        """Return metadata-only snapshot; source payloads are deliberately not stored."""
        with self._lock:
            return {
                "entries": [self._entry_dict(e) for e in sorted(self._entries.values(), key=lambda x: x.entry_id)],
                "holds": [self._hold_dict(h) for h in sorted(self._holds.values(), key=lambda x: x.hold_id)],
            }

    @staticmethod
    def _normalize_text_items(values: Iterable[str], *, error: str,
                               max_items: int, max_length: int,
                               allow_empty: bool = False) -> tuple[str, ...]:
        if isinstance(values, str) or not isinstance(values, Iterable):
            raise GammaIndexError(error)
        # Read at most max_items + 1 elements. This bounds hostile or accidental
        # unbounded iterators instead of materializing an arbitrarily large iterable.
        normalized = tuple(islice(iter(values), max_items + 1))
        if len(normalized) > max_items:
            raise GammaIndexError("ITEM_LIMIT_EXCEEDED")
        if any(not isinstance(value, str) or len(value) > max_length
               or (not allow_empty and not value.strip()) for value in normalized):
            raise GammaIndexError(error)
        cleaned = tuple(value.strip() for value in normalized)
        if not allow_empty and any(not value for value in cleaned):
            raise GammaIndexError(error)
        return cleaned

    @staticmethod
    def _validate_entry(entry: GammaEntry) -> GammaEntry:
        if not isinstance(entry, GammaEntry):
            raise GammaIndexError("INVALID_ENTRY_TYPE")
        limits = {
            "entry_id": 128, "resource_id": 256, "version": 64,
            "resource_kind": 64, "scope": 128, "source_ref": 2048,
        }
        for field_name, max_length in limits.items():
            value = getattr(entry, field_name)
            if not isinstance(value, str) or not value.strip() or len(value) > max_length:
                raise GammaIndexError(f"INVALID_{field_name.upper()}")
        if not _ID_RE.fullmatch(entry.entry_id):
            raise GammaIndexError("INVALID_ENTRY_ID")
        if not isinstance(entry.content_digest, str) or not _DIGEST_RE.fullmatch(entry.content_digest):
            raise GammaIndexError("INVALID_CONTENT_DIGEST")
        if entry.source_status not in ("VERIFIED", "UNVERIFIED", "FAILED"):
            raise GammaIndexError("INVALID_SOURCE_STATUS")
        if not isinstance(entry.status, EntryStatus):
            raise GammaIndexError("INVALID_ENTRY_STATUS")
        # Entry metadata is a finite sequence, not a streaming query input. Requiring
        # tuple/list prevents one-shot generators and unordered sets from changing the
        # indexed record between validation and registration.
        if isinstance(entry.claims, str) or not isinstance(entry.claims, (tuple, list)):
            raise GammaIndexError("INVALID_CLAIMS")
        if isinstance(entry.tags, str) or not isinstance(entry.tags, (tuple, list)):
            raise GammaIndexError("INVALID_TAGS")
        claims = GammaIndex._normalize_text_items(
            entry.claims, error="INVALID_CLAIMS", max_items=256, max_length=2000
        )
        tags = GammaIndex._normalize_text_items(
            entry.tags, error="INVALID_TAGS", max_items=128, max_length=64
        )
        if entry.created_at is not None:
            if not isinstance(entry.created_at, str) or not entry.created_at.strip():
                raise GammaIndexError("INVALID_CREATED_AT")
            try:
                parsed = datetime.fromisoformat(entry.created_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise GammaIndexError("INVALID_CREATED_AT") from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise GammaIndexError("CREATED_AT_MUST_INCLUDE_TIMEZONE")
        return replace(entry, claims=claims, tags=tags)

    @staticmethod
    def _entry_dict(e: GammaEntry) -> dict:
        return {"entry_id": e.entry_id, "resource_id": e.resource_id, "version": e.version,
                "resource_kind": e.resource_kind, "scope": e.scope,
                "content_digest": e.content_digest, "source_ref": e.source_ref,
                "source_status": e.source_status, "status": e.status.value,
                "claims": list(e.claims), "tags": list(e.tags), "created_at": e.created_at}

    @staticmethod
    def _hold_dict(h: HoldRecord) -> dict:
        return {"hold_id": h.hold_id, "entry_id": h.entry_id, "reason": h.reason.value,
                "open_questions": list(h.open_questions), "preserved_refs": list(h.preserved_refs),
                "opened_at": h.opened_at, "revisit_trigger": h.revisit_trigger,
                "status": h.status.value, "resolution": h.resolution,
                "resolution_evidence_ref": h.resolution_evidence_ref, "closed_at": h.closed_at}
