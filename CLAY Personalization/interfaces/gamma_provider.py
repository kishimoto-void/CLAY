"""Host-facing protocols for a future Gamma task-profile adapter.

This file contains interfaces only. It performs no network I/O, authentication,
permission checks, persistence, profile activation, or Delta notification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, Sequence


@dataclass(frozen=True)
class GammaProfileDescriptor:
    profile_id: str
    profile_version: str
    resource_ref: str
    etag: str | None = None


@dataclass(frozen=True)
class SourceVerification:
    status: Literal["verified", "unverified", "failed"]
    evidence_ref: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PermissionDecision:
    status: Literal["approved", "not_required", "pending", "denied"]
    scope: str
    evidence_ref: str | None = None


@dataclass(frozen=True)
class CapabilityDecision:
    available: tuple[str, ...]
    missing: tuple[str, ...]
    evidence_ref: str | None = None


@dataclass(frozen=True)
class ActivationReceipt:
    profile_id: str
    profile_version: str
    profile_digest: str
    activation_scope: Literal["current_task_session"]
    activated_at: str
    host_event_ref: str


class GammaIndexProvider(Protocol):
    """Adapter for resolving and retrieving a task profile from Gamma Index."""

    def resolve_profile(
        self, profile_id: str, version: str | None = None
    ) -> Sequence[GammaProfileDescriptor]:
        """Return zero, one, or multiple exact candidates; never silently pick among ambiguous results."""
        ...

    def fetch_profile(self, resource_ref: str) -> bytes:
        """Fetch raw profile bytes for the exact resource reference."""
        ...


class ProfileTrustVerifier(Protocol):
    """Trusted host-side source verifier; a profile's own claims are not proof."""

    def verify_source(
        self, descriptor: GammaProfileDescriptor, raw_profile: bytes
    ) -> SourceVerification:
        ...


class ProfileRuntimeHost(Protocol):
    """Host operations required before/after profile activation."""

    def check_permission(self, activation_scope: str) -> PermissionDecision:
        ...

    def check_capabilities(self, required: Sequence[str]) -> CapabilityDecision:
        ...

    def activate_overlay_atomically(
        self, profile: dict, composed_overlay: dict
    ) -> ActivationReceipt:
        """Commit all overlay values together or leave the prior active state untouched."""
        ...

    def deactivate_overlay(self, profile_id: str) -> bool:
        ...

    def emit_delta_event(self, event_type: str, payload: dict) -> str:
        """Publish a host-confirmed lifecycle event; return an event reference."""
        ...
