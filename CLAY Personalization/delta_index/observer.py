"""Delta Index: capture -> compare -> reconcile, with observer-only authority."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
import re
from threading import RLock
from typing import Optional

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
_MAX_OBSERVATIONS = 10_000
_MAX_EVENTS = 10_000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DeltaError(ValueError):
    pass


class DeltaStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    HELD = "HELD"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class DeltaKind(str, Enum):
    BASELINE_CANDIDATE = "BASELINE_CANDIDATE"
    CHANGE_CANDIDATE = "CHANGE_CANDIDATE"
    NO_CHANGE = "NO_CHANGE"


@dataclass(frozen=True)
class Snapshot:
    target_id: str
    version: str
    digest: str
    source_ref: str
    observed_at: Optional[str] = None


@dataclass(frozen=True)
class DeltaObservation:
    """Captured host observation awaiting comparison; never changes current state."""
    observation_id: str
    snapshot: Snapshot
    captured_at: str
    event_id: Optional[str] = None


@dataclass(frozen=True)
class DeltaEvent:
    event_id: str
    target_id: str
    kind: DeltaKind
    status: DeltaStatus
    prior_version: Optional[str]
    prior_digest: Optional[str]
    prior_source_ref: Optional[str]
    candidate_version: str
    candidate_digest: str
    source_ref: str
    observed_at: str
    hold_reason: Optional[str] = None
    hold_source: Optional[str] = None
    open_questions: tuple[str, ...] = ()
    resolution: Optional[str] = None
    evidence_ref: Optional[str] = None
    reconciled_at: Optional[str] = None


class DeltaObserver:
    """Observer-only three-phase Delta index.

    1. capture(): retain a validated observation, without classifying or mutation.
    2. compare(): compare the observation with the last reconciled snapshot and emit
       an event; no candidate becomes current in this phase.
    3. reconcile(): explicitly accept/reject/supersede an unresolved event. Accepting
       updates only Delta's recorded current snapshot, never a live resource/profile.

    All state is in-memory. Evidence references and source labels are opaque pointers;
    they are not authenticated or independently verified by this class. Hold origin is
    typed so caller-created holds cannot be mistaken for automatic competition holds.
    """

    def __init__(self) -> None:
        self._current: dict[str, Snapshot] = {}
        self._observations: dict[str, DeltaObservation] = {}
        self._events: dict[str, DeltaEvent] = {}
        self._next_observation_id = 1
        self._next_event_id = 1
        self._lock = RLock()

    def capture(self, snapshot: Snapshot, observation_id: Optional[str] = None) -> DeltaObservation:
        """Phase D1: capture a snapshot. It does not create a change event or update current."""
        self._validate_snapshot(snapshot)
        if observation_id is not None and (not isinstance(observation_id, str)
                                           or not _ID_RE.fullmatch(observation_id)):
            raise DeltaError("INVALID_OBSERVATION_ID")
        captured_at = _now()
        observed_at = snapshot.observed_at or captured_at
        normalized_snapshot = replace(snapshot, observed_at=observed_at)
        with self._lock:
            if observation_id is None:
                observation_id = f"observation-{self._next_observation_id:06d}"
                self._next_observation_id += 1
            existing = self._observations.get(observation_id)
            if existing is not None:
                old = existing.snapshot
                same_payload = (
                    old.target_id == normalized_snapshot.target_id
                    and old.version == normalized_snapshot.version
                    and old.digest == normalized_snapshot.digest
                    and old.source_ref == normalized_snapshot.source_ref
                    and (snapshot.observed_at is None or old.observed_at == snapshot.observed_at)
                )
                if same_payload:
                    return existing
                raise DeltaError("OBSERVATION_ID_COLLISION")
            if len(self._observations) >= _MAX_OBSERVATIONS:
                raise DeltaError("OBSERVATION_LIMIT_EXCEEDED")
            observation = DeltaObservation(
                observation_id=observation_id,
                snapshot=normalized_snapshot,
                captured_at=captured_at,
            )
            self._observations[observation_id] = observation
            return observation

    def compare(self, observation_id: str) -> DeltaEvent:
        """Phase D2: classify one captured observation against reconciled current state."""
        if not isinstance(observation_id, str) or not _ID_RE.fullmatch(observation_id):
            raise DeltaError("INVALID_OBSERVATION_ID")
        with self._lock:
            observation = self._observations.get(observation_id)
            if observation is None:
                raise DeltaError("OBSERVATION_NOT_FOUND")
            if observation.event_id is not None:
                # Idempotent repeat: comparison cannot generate duplicate events.
                return self._events[observation.event_id]
            snapshot = observation.snapshot
            current = self._current.get(snapshot.target_id)
            if current is None:
                kind = DeltaKind.BASELINE_CANDIDATE
                prior_version = prior_digest = prior_source_ref = None
            elif (current.version == snapshot.version and current.digest == snapshot.digest
                  and current.source_ref == snapshot.source_ref):
                kind = DeltaKind.NO_CHANGE
                prior_version, prior_digest, prior_source_ref = (
                    current.version, current.digest, current.source_ref
                )
            else:
                kind = DeltaKind.CHANGE_CANDIDATE
                prior_version, prior_digest, prior_source_ref = (
                    current.version, current.digest, current.source_ref
                )

            competing = any(
                e.target_id == snapshot.target_id
                and e.status in (DeltaStatus.PENDING_REVIEW, DeltaStatus.HELD)
                # A stale-base candidate is retained for history/review, but it must
                # not deadlock a fresh observation made against the new current base.
                and e.hold_source != "STALE_BASE"
                for e in self._events.values()
            )
            if kind is DeltaKind.NO_CHANGE:
                status = DeltaStatus.CONFIRMED
            elif competing:
                status = DeltaStatus.HELD
            else:
                status = DeltaStatus.PENDING_REVIEW

            if len(self._events) >= _MAX_EVENTS:
                raise DeltaError("EVENT_LIMIT_EXCEEDED")
            event_id = f"delta-{self._next_event_id:06d}"
            self._next_event_id += 1
            event = DeltaEvent(
                event_id=event_id, target_id=snapshot.target_id, kind=kind, status=status,
                prior_version=prior_version, prior_digest=prior_digest,
                prior_source_ref=prior_source_ref,
                candidate_version=snapshot.version, candidate_digest=snapshot.digest,
                source_ref=snapshot.source_ref, observed_at=snapshot.observed_at or observation.captured_at,
                hold_reason="COMPETING_CANDIDATES" if competing and kind is not DeltaKind.NO_CHANGE else None,
                hold_source="SYSTEM_COMPETITION" if competing and kind is not DeltaKind.NO_CHANGE else None,
                open_questions=(
                    ("Confirm source authority and intended baseline before accepting this snapshot.",)
                    if kind is DeltaKind.BASELINE_CANDIDATE else
                    ("Confirm that this change is intended and compatible before accepting it.",)
                    if kind is DeltaKind.CHANGE_CANDIDATE else
                    ("Version, digest, and source reference match the current snapshot; no change was applied.",)
                ),
            )
            if competing and kind is not DeltaKind.NO_CHANGE:
                event = replace(event, open_questions=tuple(dict.fromkeys((
                    *event.open_questions,
                    "Which candidate is authoritative for this target?",
                ))))
            self._events[event_id] = event
            self._observations[observation_id] = replace(observation, event_id=event_id)
            return event

    def observe(self, snapshot: Snapshot, observation_id: Optional[str] = None) -> DeltaEvent:
        """Compatibility convenience method: execute capture then compare."""
        observation = self.capture(snapshot, observation_id=observation_id)
        return self.compare(observation.observation_id)

    def hold(self, event_id: str, reason: str, open_questions: tuple[str, ...]) -> DeltaEvent:
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 256:
            raise DeltaError("HOLD_REQUIRES_REASON_AND_OPEN_QUESTION")
        if (isinstance(open_questions, str) or not isinstance(open_questions, (tuple, list))
                or not open_questions or len(open_questions) > 64
                or any(not isinstance(q, str) or not q.strip() or len(q) > 2000
                       for q in open_questions)):
            raise DeltaError("HOLD_REQUIRES_REASON_AND_OPEN_QUESTION")
        with self._lock:
            event = self._require_unresolved(event_id)
            held = replace(event, status=DeltaStatus.HELD, hold_reason=reason.strip(),
                           hold_source="USER",
                           open_questions=tuple(q.strip() for q in open_questions))
            self._events[event_id] = held
            return held

    def reconcile(self, event_id: str, decision: str, resolution: str,
                  evidence_ref: str) -> DeltaEvent:
        """Phase D3: evidence-referenced reconciliation; acceptance uses a stale-base guard."""
        allowed = {"ACCEPT_CANDIDATE", "REJECT_CANDIDATE", "SUPERSEDE_CANDIDATE"}
        if not isinstance(decision, str) or decision not in allowed:
            raise DeltaError("INVALID_RECONCILIATION_DECISION")
        if (not isinstance(resolution, str) or not resolution.strip() or len(resolution) > 2000
                or not isinstance(evidence_ref, str) or not evidence_ref.strip()
                or len(evidence_ref) > 2048):
            raise DeltaError("RECONCILIATION_REQUIRES_EVIDENCE_AND_RATIONALE")
        with self._lock:
            event = self._require_unresolved(event_id)
            if decision == "ACCEPT_CANDIDATE":
                current = self._current.get(event.target_id)
                base_matches = (
                    current is None and event.prior_version is None
                    and event.prior_digest is None and event.prior_source_ref is None
                ) or (
                    current is not None
                    and current.version == event.prior_version
                    and current.digest == event.prior_digest
                    and current.source_ref == event.prior_source_ref
                )
                if not base_matches:
                    raise DeltaError("STALE_CANDIDATE_REQUIRES_REOBSERVATION")
                status = DeltaStatus.CONFIRMED
                self._current[event.target_id] = Snapshot(
                    target_id=event.target_id, version=event.candidate_version,
                    digest=event.candidate_digest, source_ref=event.source_ref,
                    observed_at=event.observed_at,
                )
            elif decision == "REJECT_CANDIDATE":
                status = DeltaStatus.REJECTED
            else:
                status = DeltaStatus.SUPERSEDED
            reconciled = replace(event, status=status, resolution=resolution.strip(),
                                 evidence_ref=evidence_ref.strip(), reconciled_at=_now(),
                                 hold_source=None, open_questions=())
            self._events[event_id] = reconciled
            # Resolve the competing-candidate lifecycle without making a content decision.
            # A changed base makes every other unresolved candidate stale. If a candidate
            # was only held because this event competed with it and this event is rejected
            # or superseded, the unchanged base permits it to return to review.
            for other_id, other in tuple(self._events.items()):
                if (other_id == event_id or other.target_id != event.target_id
                        or other.status not in (DeltaStatus.PENDING_REVIEW, DeltaStatus.HELD)):
                    continue
                if decision == "ACCEPT_CANDIDATE":
                    questions = tuple(dict.fromkeys((
                        *other.open_questions,
                        *(
                            (f"Previous hold reason: {other.hold_reason}",)
                            if other.hold_reason and other.hold_source != "STALE_BASE"
                            else ()
                        ),
                        "Re-observe this candidate against the newly confirmed current snapshot, then compare again.",
                    )))
                    if other.hold_source == "USER":
                        # Never relax a caller-imposed hold as a side effect of another
                        # candidate winning. Preserve it; the caller must explicitly resolve it.
                        self._events[other_id] = replace(other, open_questions=questions)
                    else:
                        self._events[other_id] = replace(
                            other, status=DeltaStatus.HELD,
                            hold_reason="COMPETING_CANDIDATE_REQUIRES_REBASE",
                            hold_source="STALE_BASE",
                            open_questions=questions,
                        )
                elif (other.status is DeltaStatus.HELD
                      and other.hold_source == "SYSTEM_COMPETITION"):
                    questions = tuple(dict.fromkeys((
                        *other.open_questions,
                        "The competing candidate was rejected or superseded; review this candidate against the unchanged current snapshot.",
                    )))
                    self._events[other_id] = replace(
                        other, status=DeltaStatus.PENDING_REVIEW,
                        hold_reason=None, hold_source=None,
                        open_questions=questions,
                    )
            return reconciled

    def current(self, target_id: str) -> Optional[Snapshot]:
        with self._lock:
            return self._current.get(target_id)

    def get_observation(self, observation_id: str) -> Optional[DeltaObservation]:
        with self._lock:
            return self._observations.get(observation_id)

    def observation_log(self) -> tuple[DeltaObservation, ...]:
        with self._lock:
            return tuple(self._observations.values())

    def get_event(self, event_id: str) -> Optional[DeltaEvent]:
        with self._lock:
            return self._events.get(event_id)

    def pending(self, target_id: Optional[str] = None) -> tuple[DeltaEvent, ...]:
        with self._lock:
            return tuple(e for e in self._events.values()
                         if e.status in (DeltaStatus.PENDING_REVIEW, DeltaStatus.HELD)
                         and (target_id is None or e.target_id == target_id))

    def event_log(self) -> tuple[DeltaEvent, ...]:
        with self._lock:
            return tuple(self._events.values())

    @staticmethod
    def _validate_snapshot(snapshot: Snapshot) -> None:
        if not isinstance(snapshot, Snapshot):
            raise DeltaError("INVALID_SNAPSHOT_TYPE")
        limits = {"target_id": 256, "version": 64, "source_ref": 2048}
        for name, max_length in limits.items():
            value = getattr(snapshot, name)
            if not isinstance(value, str) or not value.strip() or len(value) > max_length:
                raise DeltaError(f"INVALID_{name.upper()}")
        if not isinstance(snapshot.digest, str) or not _DIGEST_RE.fullmatch(snapshot.digest):
            raise DeltaError("INVALID_DIGEST")
        if snapshot.observed_at is not None:
            if not isinstance(snapshot.observed_at, str) or not snapshot.observed_at.strip():
                raise DeltaError("INVALID_OBSERVED_AT")
            if not _RFC3339_RE.fullmatch(snapshot.observed_at):
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?", snapshot.observed_at):
                    raise DeltaError("OBSERVED_AT_MUST_INCLUDE_TIMEZONE")
                raise DeltaError("INVALID_OBSERVED_AT")
            try:
                parsed = datetime.fromisoformat(snapshot.observed_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise DeltaError("INVALID_OBSERVED_AT") from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise DeltaError("OBSERVED_AT_MUST_INCLUDE_TIMEZONE")

    def _require_unresolved(self, event_id: str) -> DeltaEvent:
        if not isinstance(event_id, str) or not _ID_RE.fullmatch(event_id):
            raise DeltaError("INVALID_EVENT_ID")
        event = self._events.get(event_id)
        if event is None:
            raise DeltaError("EVENT_NOT_FOUND")
        if event.status not in (DeltaStatus.PENDING_REVIEW, DeltaStatus.HELD):
            raise DeltaError("EVENT_NOT_UNRESOLVED")
        return event
