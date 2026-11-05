"""Interfaces only: safety decisions must be supplied by validated host policy."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence


class SafetyVerdict(str, Enum):
    ALLOW = "ALLOW"
    CONDITIONAL = "CONDITIONAL"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SafetyAssessment:
    verdict: SafetyVerdict
    reasons: tuple[str, ...]
    required_conditions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    reassessment_trigger: str | None = None


@dataclass(frozen=True)
class CapabilityDeclaration:
    capability: str
    status: str  # CAN / CONDITIONAL / UNKNOWN / CANNOT / PROHIBITED
    equipment_ref: str | None = None
    evidence_ref: str | None = None
    constraints: tuple[str, ...] = ()


class RiskBoundaryEngine(Protocol):
    def assess(self, action: str, context_refs: Sequence[str]) -> SafetyAssessment:
        """Return a risk boundary assessment; no profile may weaken its result."""
        ...


class RecoveryPathEngine(Protocol):
    def propose_alternatives(self, blocked_goal: str, context_refs: Sequence[str]) -> Sequence[str]:
        """Propose bounded alternatives; proposal is not authorization or execution."""
        ...


class SituationalVerification(Protocol):
    def verify(self, required_observations: Sequence[str]) -> SafetyAssessment:
        ...


class CapabilityRegistry(Protocol):
    def declare(self, capability: str) -> CapabilityDeclaration:
        ...
