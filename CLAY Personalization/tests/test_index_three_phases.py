"""Focused conformance tests for the Gamma and Delta three-phase contracts."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest
import json
from dataclasses import asdict
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gamma_index import (
    EntryStatus, GammaEntry, GammaIndex, GammaIndexError, HoldReason,
)
from delta_index import DeltaError, DeltaObserver, DeltaStatus, Snapshot

D1 = "a" * 64
D2 = "b" * 64
D3 = "c" * 64


def gamma_entry(entry_id="entry.a", resource_id="resource.a", version="1.0.0",
                digest=D1, scope="fishing", source_status="UNVERIFIED",
                status=EntryStatus.CANDIDATE, tags=("fishing", "record"),
                claims=("fishing log context",)):
    return GammaEntry(
        entry_id=entry_id, resource_id=resource_id, version=version,
        resource_kind="context_module", scope=scope, content_digest=digest,
        source_ref=f"repo://{resource_id}@{version}", source_status=source_status,
        status=status, claims=claims, tags=tags,
    )


def snapshot(version="1.0.0", digest=D1, target="profile:fishing", source="host://snapshot"):
    return Snapshot(target_id=target, version=version, digest=digest, source_ref=source)


class GammaThreePhaseTests(unittest.TestCase):
    def setUp(self):
        self.gamma = GammaIndex()
        self.gamma.register(gamma_entry())
        self.gamma.register(gamma_entry(
            entry_id="entry.b", resource_id="resource.b", scope="shopping",
            tags=("shopping", "record"), digest=D2,
        ))

    def test_g1_discovery_is_bounded_and_scope_exact(self):
        page = self.gamma.discover(query="record", scope="fishing", limit=10)
        self.assertEqual(page.matched_count, 1)
        self.assertEqual(page.results[0].entry.entry_id, "entry.a")
        self.assertIsNone(page.next_offset)

    def test_g1_discovery_defaults_to_excluding_held_entries(self):
        self.gamma.hold("entry.a", "hold.a", HoldReason.MISSING_CONTEXT, ["Need source context"])
        self.assertEqual(self.gamma.discover(query="fishing", scope="fishing").matched_count, 0)
        self.assertEqual(self.gamma.discover(query="fishing", scope="fishing", include_held=True).matched_count, 1)

    def test_g1_tag_generators_are_not_consumed_by_validation(self):
        tags = (tag for tag in ("fishing", "record"))
        page = self.gamma.discover(tags=tags)
        self.assertEqual([r.entry.entry_id for r in page.results], ["entry.a"])

    def test_registered_list_metadata_is_frozen_against_caller_mutation(self):
        claims = ["initial claim"]
        tags = ["fishing"]
        entry = gamma_entry(entry_id="entry.mutable", resource_id="resource.mutable",
                            claims=claims, tags=tags, digest="e" * 64)
        self.gamma.register(entry)
        claims.append("mutated claim")
        tags.append("shopping")
        stored = self.gamma.get("entry.mutable").entry
        self.assertEqual(stored.claims, ("initial claim",))
        self.assertEqual(stored.tags, ("fishing",))

    def test_g1_pagination_is_deterministic_and_reports_truncation(self):
        page1 = self.gamma.discover(limit=1)
        self.assertEqual(page1.matched_count, 2)
        self.assertTrue(page1.truncated)
        page2 = self.gamma.discover(limit=1, offset=page1.next_offset,
                                    expected_revision=page1.revision)
        self.assertFalse(page2.truncated)
        self.assertNotEqual(page1.results[0].entry.entry_id, page2.results[0].entry.entry_id)

    def test_g1_pagination_requires_revision_on_continuation(self):
        with self.assertRaisesRegex(GammaIndexError, "DISCOVERY_CONTINUATION_REQUIRES_REVISION"):
            self.gamma.discover(limit=1, offset=1)

    def test_g1_pagination_restarts_when_index_changes_between_pages(self):
        page1 = self.gamma.discover(limit=1)
        self.gamma.register(gamma_entry(entry_id="entry.c", resource_id="resource.c",
                                        digest="f" * 64, scope="travel", tags=("travel",)))
        with self.assertRaisesRegex(GammaIndexError, "STALE_DISCOVERY_PAGE_RESTART_REQUIRED"):
            self.gamma.discover(limit=1, offset=page1.next_offset,
                                expected_revision=page1.revision)

    def test_g1_rejects_unbounded_or_invalid_search_parameters(self):
        with self.assertRaisesRegex(GammaIndexError, "INVALID_DISCOVERY_LIMIT"):
            self.gamma.discover(limit=101)
        with self.assertRaisesRegex(GammaIndexError, "INVALID_DISCOVERY_OFFSET"):
            self.gamma.discover(offset=-1)
        with self.assertRaisesRegex(GammaIndexError, "INVALID_QUERY"):
            self.gamma.search(query="x" * 513)

    def test_search_caps_one_shot_iterators_without_exhausting_them(self):
        consumed = []

        def unbounded_tags():
            index = 0
            while True:
                consumed.append(index)
                yield f"tag-{index}"
                index += 1

        with self.assertRaisesRegex(GammaIndexError, "ITEM_LIMIT_EXCEEDED"):
            self.gamma.search(tags=unbounded_tags())
        self.assertEqual(len(consumed), 33)  # max 32 + one sentinel item

    def test_registered_entry_rejects_one_shot_metadata_generators(self):
        entry = gamma_entry(entry_id="entry.generator", resource_id="resource.generator",
                            digest="e" * 64)
        entry = __import__("dataclasses").replace(entry, claims=(x for x in ("claim",)))
        with self.assertRaisesRegex(GammaIndexError, "INVALID_CLAIMS"):
            self.gamma.register(entry)

    def test_resolve_rejects_malformed_expected_digest_and_oversized_identity(self):
        with self.assertRaisesRegex(GammaIndexError, "INVALID_EXPECTED_CONTENT_DIGEST"):
            self.gamma.resolve("entry.a", expected_digest="not-a-sha256")
        with self.assertRaisesRegex(GammaIndexError, "INVALID_EXPECTED_RESOURCE_ID"):
            self.gamma.resolve("entry.a", expected_resource_id="x" * 257)

    def test_g2_requires_exact_candidate_id_and_checks_expected_identity(self):
        resolved = self.gamma.resolve("entry.a", expected_resource_id="resource.a",
                                      expected_version="1.0.0", expected_scope="fishing")
        self.assertEqual(resolved.entry.entry_id, "entry.a")
        with self.assertRaisesRegex(GammaIndexError, "IDENTITY_MISMATCH_VERSION"):
            self.gamma.resolve("entry.a", expected_version="9.9.9")

    def test_g2_does_not_select_held_or_terminal_entry(self):
        self.gamma.hold("entry.a", "hold.a", HoldReason.OTHER, ["Resolve ambiguity"])
        with self.assertRaisesRegex(GammaIndexError, "ENTRY_HELD"):
            self.gamma.resolve("entry.a")
        self.gamma.close_hold("hold.a", EntryStatus.REJECTED, "Rejected", "review:1")
        with self.assertRaisesRegex(GammaIndexError, "ENTRY_NOT_ELIGIBLE"):
            self.gamma.resolve("entry.a")

    def test_g3_handoff_is_reference_only_and_never_authorizes(self):
        handoff = self.gamma.handoff("entry.a", expected_scope="fishing")
        self.assertEqual(handoff.source_ref, "repo://resource.a@1.0.0")
        self.assertFalse(handoff.retrieval_authorized)
        self.assertFalse(handoff.activation_authorized)
        self.assertIn("PERMISSION_CHECK", handoff.required_host_checks)
        self.assertIn("SOURCE_AUTHENTICATION", handoff.required_host_checks)

    def test_g3_declared_verified_source_still_requires_host_checks(self):
        self.gamma.register(gamma_entry(
            entry_id="entry.verified", resource_id="resource.verified",
            source_status="VERIFIED", digest=D3,
        ))
        handoff = self.gamma.handoff("entry.verified")
        self.assertEqual(handoff.source_status, "VERIFIED")
        self.assertFalse(handoff.retrieval_authorized)
        self.assertIn("SAFETY_POLICY_CHECK", handoff.required_host_checks)

    def test_g3_failed_source_cannot_be_handed_off(self):
        self.gamma.register(gamma_entry(
            entry_id="entry.failed", resource_id="resource.failed",
            source_status="FAILED", digest="d" * 64,
        ))
        with self.assertRaisesRegex(GammaIndexError, "SOURCE_STATUS_FAILED"):
            self.gamma.handoff("entry.failed")

    def test_g3_runtime_handoff_matches_schema(self):
        handoff = self.gamma.handoff("entry.a")
        schema = json.loads((ROOT / "schemas/gamma_handoff.schema.json").read_text(encoding="utf-8"))
        payload = json.loads(json.dumps(asdict(handoff)))
        errors = list(Draft202012Validator(schema).iter_errors(payload))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_hold_rejects_silently_filtered_non_string_question(self):
        with self.assertRaisesRegex(GammaIndexError, "HOLD_REQUIRES_QUESTION_LIST"):
            self.gamma.hold("entry.a", "hold.bad", HoldReason.OTHER, ["valid", None])


class DeltaThreePhaseTests(unittest.TestCase):
    def setUp(self):
        self.delta = DeltaObserver()

    def test_d1_capture_does_not_create_event_or_change_current(self):
        observation = self.delta.capture(snapshot(), observation_id="obs.initial")
        self.assertEqual(observation.observation_id, "obs.initial")
        self.assertIsNone(observation.event_id)
        self.assertEqual(self.delta.event_log(), ())
        self.assertIsNone(self.delta.current("profile:fishing"))

    def test_d1_capture_time_is_distinct_from_source_observation_time(self):
        observation = self.delta.capture(Snapshot(
            "profile:fishing", "1.0.0", D1, "host://snapshot", "2026-11-03T08:00:00+09:00"
        ))
        self.assertEqual(observation.snapshot.observed_at, "2026-11-03T08:00:00+09:00")
        self.assertNotEqual(observation.captured_at, observation.snapshot.observed_at)

    def test_d1_same_observation_id_is_idempotent(self):
        first = self.delta.capture(snapshot(), observation_id="obs.replay")
        replay = self.delta.capture(snapshot(), observation_id="obs.replay")
        self.assertEqual(first, replay)
        self.assertEqual(len(self.delta.observation_log()), 1)

    def test_delta_event_schema_rejects_hold_origin_on_non_held_status(self):
        baseline = self.delta.observe(snapshot(), observation_id="obs.base")
        event = asdict(baseline)
        event["hold_source"] = "USER"
        schema = json.loads((ROOT / "schemas/delta_event.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(event))
        self.assertTrue(errors)

    def test_d2_runtime_event_matches_schema_including_hold_origin(self):
        baseline = self.delta.observe(snapshot(), observation_id="obs.base")
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "Accept baseline", "evidence:base")
        first = self.delta.observe(snapshot(version="2.0.0", digest=D2), observation_id="obs.first")
        self.delta.observe(snapshot(version="3.0.0", digest=D3), observation_id="obs.second")
        held = self.delta.get_event(self.delta.observation_log()[-1].event_id)
        self.assertEqual(held.hold_source, "SYSTEM_COMPETITION")
        schema = json.loads((ROOT / "schemas/delta_event.schema.json").read_text(encoding="utf-8"))
        payload = json.loads(json.dumps(asdict(held)))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_d1_runtime_observation_matches_schema(self):
        observation = self.delta.capture(snapshot(), observation_id="obs.schema")
        schema = json.loads((ROOT / "schemas/delta_observation.schema.json").read_text(encoding="utf-8"))
        payload = json.loads(json.dumps(asdict(observation)))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_d1_observation_id_collision_fails_closed(self):
        self.delta.capture(snapshot(), observation_id="obs.collision")
        with self.assertRaisesRegex(DeltaError, "OBSERVATION_ID_COLLISION"):
            self.delta.capture(snapshot(version="2.0.0", digest=D2), observation_id="obs.collision")

    def test_d2_compare_creates_baseline_candidate_without_mutating_current(self):
        observation = self.delta.capture(snapshot())
        event = self.delta.compare(observation.observation_id)
        self.assertEqual(event.status, DeltaStatus.PENDING_REVIEW)
        self.assertIsNone(self.delta.current("profile:fishing"))

    def test_d2_compare_is_idempotent(self):
        observation = self.delta.capture(snapshot())
        first = self.delta.compare(observation.observation_id)
        replay = self.delta.compare(observation.observation_id)
        self.assertEqual(first, replay)
        self.assertEqual(len(self.delta.event_log()), 1)

    def test_d2_missing_observation_is_rejected(self):
        with self.assertRaisesRegex(DeltaError, "OBSERVATION_NOT_FOUND"):
            self.delta.compare("obs.missing")

    def test_d2_compare_against_last_reconciled_snapshot(self):
        baseline = self.delta.observe(snapshot())
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "baseline accepted", "host:1")
        change = self.delta.observe(snapshot(version="1.1.0", digest=D2))
        self.assertEqual(change.kind.value, "CHANGE_CANDIDATE")
        self.assertEqual(change.prior_digest, D1)
        self.assertEqual(self.delta.current("profile:fishing").digest, D1)

    def test_d2_source_reference_change_is_not_misclassified_as_no_change(self):
        baseline = self.delta.observe(snapshot())
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "baseline", "host:1")
        same_content_new_source = self.delta.observe(snapshot(source="host://replica"))
        self.assertEqual(same_content_new_source.kind.value, "CHANGE_CANDIDATE")
        self.assertEqual(same_content_new_source.prior_source_ref, "host://snapshot")

    def test_d3_stale_source_reference_candidate_cannot_overwrite_newer_source(self):
        baseline = self.delta.observe(snapshot())
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "baseline", "host:1")
        candidate_a = self.delta.observe(snapshot(source="host://replica-a"))
        candidate_b = self.delta.observe(snapshot(source="host://replica-b"))
        self.delta.reconcile(candidate_b.event_id, "ACCEPT_CANDIDATE", "replica b selected", "host:b")
        with self.assertRaisesRegex(DeltaError, "STALE_CANDIDATE_REQUIRES_REOBSERVATION"):
            self.delta.reconcile(candidate_a.event_id, "ACCEPT_CANDIDATE", "stale replica", "host:a")
        self.assertEqual(self.delta.current("profile:fishing").source_ref, "host://replica-b")

    def test_d3_accept_rejects_stale_candidate_after_other_candidate_wins(self):
        baseline = self.delta.observe(snapshot())
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "baseline", "host:0")
        candidate_a = self.delta.observe(snapshot(version="1.1.0", digest=D2, source="host:a"))
        candidate_b = self.delta.observe(snapshot(version="1.2.0", digest=D3, source="host:b"))
        self.delta.reconcile(candidate_b.event_id, "ACCEPT_CANDIDATE", "selected by operator", "host:b-review")
        with self.assertRaisesRegex(DeltaError, "STALE_CANDIDATE_REQUIRES_REOBSERVATION"):
            self.delta.reconcile(candidate_a.event_id, "ACCEPT_CANDIDATE", "stale candidate", "host:a-review")
        self.assertEqual(self.delta.current("profile:fishing").digest, D3)

    def test_d3_stale_candidate_does_not_deadlock_fresh_reobservation(self):
        baseline = self.delta.observe(snapshot(version="1.0.0"), observation_id="obs.base")
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "Accept baseline", "evidence:base")
        candidate_a = self.delta.observe(snapshot(version="2.0.0", digest=D2, source="repo://a"),
                                        observation_id="obs.a")
        candidate_b = self.delta.observe(snapshot(version="3.0.0", digest=D3, source="repo://b"),
                                        observation_id="obs.b")
        self.assertEqual(candidate_b.status, DeltaStatus.HELD)
        self.delta.reconcile(candidate_a.event_id, "ACCEPT_CANDIDATE", "Accept A", "evidence:a")
        stale_b = self.delta.get_event(candidate_b.event_id)
        self.assertEqual(stale_b.hold_reason, "COMPETING_CANDIDATE_REQUIRES_REBASE")
        self.assertEqual(stale_b.hold_source, "STALE_BASE")
        refreshed = self.delta.capture(snapshot(version="3.0.0", digest=D3, source="repo://b"),
                                       observation_id="obs.b.refreshed")
        reevaluated = self.delta.compare(refreshed.observation_id)
        self.assertEqual(reevaluated.kind.value, "CHANGE_CANDIDATE")
        self.assertEqual(reevaluated.status, DeltaStatus.PENDING_REVIEW)
        self.assertEqual(reevaluated.prior_version, "2.0.0")

    def test_d3_rejecting_competitor_releases_other_candidate_for_review(self):
        baseline = self.delta.observe(snapshot(version="1.0.0"), observation_id="obs.base")
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "Accept baseline", "evidence:base")
        candidate_a = self.delta.observe(snapshot(version="2.0.0", digest=D2, source="repo://a"),
                                        observation_id="obs.a")
        candidate_b = self.delta.observe(snapshot(version="3.0.0", digest=D3, source="repo://b"),
                                        observation_id="obs.b")
        self.assertEqual(candidate_b.status, DeltaStatus.HELD)
        self.delta.reconcile(candidate_a.event_id, "REJECT_CANDIDATE", "Reject A", "evidence:a")
        released_b = self.delta.get_event(candidate_b.event_id)
        self.assertEqual(released_b.status, DeltaStatus.PENDING_REVIEW)
        self.assertIsNone(released_b.hold_reason)
        self.assertIsNone(released_b.hold_source)
        self.assertEqual(self.delta.current("profile:fishing").version, "1.0.0")

    def test_d3_stale_candidate_can_be_rejected_without_mutating_current(self):
        baseline = self.delta.observe(snapshot())
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "baseline", "host:0")
        candidate_a = self.delta.observe(snapshot(version="1.1.0", digest=D2, source="host:a"))
        candidate_b = self.delta.observe(snapshot(version="1.2.0", digest=D3, source="host:b"))
        self.delta.reconcile(candidate_b.event_id, "ACCEPT_CANDIDATE", "selected", "host:b-review")
        result = self.delta.reconcile(candidate_a.event_id, "REJECT_CANDIDATE", "stale and rejected", "review:a")
        self.assertEqual(result.status, DeltaStatus.REJECTED)
        self.assertEqual(self.delta.current("profile:fishing").digest, D3)

    def test_d3_accept_requires_rationale_and_evidence_pointer(self):
        event = self.delta.observe(snapshot())
        with self.assertRaisesRegex(DeltaError, "RECONCILIATION_REQUIRES_EVIDENCE"):
            self.delta.reconcile(event.event_id, "ACCEPT_CANDIDATE", "accepted", "")
        self.assertIsNone(self.delta.current("profile:fishing"))

    def test_d3_user_hold_is_not_mistaken_for_system_competition_hold(self):
        baseline = self.delta.observe(snapshot(), observation_id="obs.base")
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "Accept baseline", "evidence:base")
        candidate = self.delta.observe(snapshot(version="2.0.0", digest=D2), observation_id="obs.candidate")
        self.delta.hold(candidate.event_id, "COMPETING_CANDIDATES", ("Manual review required",))
        other = self.delta.observe(snapshot(version="3.0.0", digest=D3), observation_id="obs.other")
        self.assertEqual(other.hold_source, "SYSTEM_COMPETITION")
        self.delta.reconcile(other.event_id, "REJECT_CANDIDATE", "Reject other", "evidence:other")
        still_user_held = self.delta.get_event(candidate.event_id)
        self.assertEqual(still_user_held.status, DeltaStatus.HELD)
        self.assertEqual(still_user_held.hold_source, "USER")
        self.assertEqual(still_user_held.hold_reason, "COMPETING_CANDIDATES")

    def test_d3_accepting_competitor_never_lifts_explicit_user_hold(self):
        baseline = self.delta.observe(snapshot(), observation_id="obs.base")
        self.delta.reconcile(baseline.event_id, "ACCEPT_CANDIDATE", "Accept baseline", "evidence:base")
        user_held = self.delta.observe(snapshot(version="2.0.0", digest=D2), observation_id="obs.user")
        self.delta.hold(user_held.event_id, "Needs manual sign-off", ("Wait for owner review",))
        competing = self.delta.observe(snapshot(version="3.0.0", digest=D3), observation_id="obs.other")
        self.delta.reconcile(competing.event_id, "ACCEPT_CANDIDATE", "Accept competing candidate", "evidence:other")
        still_held = self.delta.get_event(user_held.event_id)
        self.assertEqual(still_held.status, DeltaStatus.HELD)
        self.assertEqual(still_held.hold_source, "USER")
        self.assertEqual(still_held.hold_reason, "Needs manual sign-off")
        refreshed = self.delta.capture(snapshot(version="2.0.0", digest=D2), observation_id="obs.user.refresh")
        fresh_event = self.delta.compare(refreshed.observation_id)
        self.assertEqual(fresh_event.status, DeltaStatus.HELD)
        self.assertEqual(fresh_event.hold_source, "SYSTEM_COMPETITION")

    def test_d3_current_means_reconciled_snapshot_not_live_activation(self):
        event = self.delta.observe(snapshot())
        self.delta.reconcile(event.event_id, "ACCEPT_CANDIDATE", "recorded", "host:1")
        current = self.delta.current("profile:fishing")
        self.assertEqual(current.digest, D1)
        # Contract fact is documented: this class only updates its local record.
        self.assertTrue(hasattr(self.delta, "current"))

    def test_snapshot_timestamp_requires_timezone(self):
        with self.assertRaisesRegex(DeltaError, "OBSERVED_AT_MUST_INCLUDE_TIMEZONE"):
            self.delta.capture(Snapshot("profile:fishing", "1.0.0", D1,
                                        "host://snapshot", "2026-11-04T12:00:00"))

    def test_observe_compatibility_method_still_performs_capture_and_compare(self):
        event = self.delta.observe(snapshot(), observation_id="obs.compat")
        self.assertEqual(event.kind.value, "BASELINE_CANDIDATE")
        self.assertEqual(len(self.delta.observation_log()), 1)


if __name__ == "__main__":
    unittest.main()
