import sys
from pathlib import Path
import unittest
import json
from dataclasses import asdict
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from delta_index import DeltaError, DeltaKind, DeltaObserver, DeltaStatus, Snapshot

D1 = "a" * 64
D2 = "b" * 64
D3 = "c" * 64


def snap(version="1.0.0", digest=D1, target="active-profile:work"):
    return Snapshot(target_id=target, version=version, digest=digest,
                    source_ref=f"gamma://work@{version}")


class DeltaIndexTests(unittest.TestCase):
    def setUp(self):
        self.delta = DeltaObserver()

    def test_first_observation_is_candidate_not_active(self):
        event = self.delta.observe(snap())
        self.assertEqual(event.kind, DeltaKind.BASELINE_CANDIDATE)
        self.assertEqual(event.status, DeltaStatus.PENDING_REVIEW)
        self.assertIsNone(self.delta.current("active-profile:work"))

    def test_accept_baseline_requires_evidence(self):
        event = self.delta.observe(snap())
        with self.assertRaisesRegex(DeltaError, "RECONCILIATION_REQUIRES_EVIDENCE"):
            self.delta.reconcile(event.event_id, "ACCEPT_CANDIDATE", "approved", "")
        self.assertIsNone(self.delta.current("active-profile:work"))

    def test_confirmed_baseline_becomes_current(self):
        event = self.delta.observe(snap())
        result = self.delta.reconcile(event.event_id, "ACCEPT_CANDIDATE",
                                     "Host verified baseline", "host-check:1")
        self.assertEqual(result.status, DeltaStatus.CONFIRMED)
        self.assertEqual(self.delta.current("active-profile:work").digest, D1)

    def test_change_does_not_mutate_current_before_reconciliation(self):
        event0 = self.delta.observe(snap())
        self.delta.reconcile(event0.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        change = self.delta.observe(snap("1.1.0", D2))
        self.assertEqual(change.kind, DeltaKind.CHANGE_CANDIDATE)
        self.assertEqual(change.status, DeltaStatus.PENDING_REVIEW)
        self.assertEqual(self.delta.current("active-profile:work").digest, D1)

    def test_hold_preserves_prior_and_candidate(self):
        base = self.delta.observe(snap())
        self.delta.reconcile(base.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        change = self.delta.observe(snap("1.1.0", D2))
        held = self.delta.hold(change.event_id, "CONFLICTING_CHANGE",
                               ("Which version is intended?",))
        self.assertEqual(held.status, DeltaStatus.HELD)
        self.assertEqual(held.prior_digest, D1)
        self.assertEqual(held.candidate_digest, D2)
        self.assertEqual(self.delta.current("active-profile:work").digest, D1)

    def test_competing_candidates_are_held_not_guessed(self):
        base = self.delta.observe(snap())
        self.delta.reconcile(base.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        one = self.delta.observe(snap("1.1.0", D2))
        two = self.delta.observe(snap("1.2.0", D3))
        self.assertEqual(one.status, DeltaStatus.PENDING_REVIEW)
        self.assertEqual(two.status, DeltaStatus.HELD)
        self.assertEqual(len(self.delta.pending("active-profile:work")), 2)

    def test_reject_candidate_keeps_active_state(self):
        base = self.delta.observe(snap())
        self.delta.reconcile(base.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        change = self.delta.observe(snap("2.0.0", D2))
        self.delta.reconcile(change.event_id, "REJECT_CANDIDATE", "invalid update", "evidence:2")
        self.assertEqual(self.delta.current("active-profile:work").digest, D1)

    def test_no_change_is_observation_only(self):
        base = self.delta.observe(snap())
        self.delta.reconcile(base.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        no_change = self.delta.observe(snap())
        self.assertEqual(no_change.kind, DeltaKind.NO_CHANGE)
        self.assertEqual(no_change.status, DeltaStatus.CONFIRMED)

    def test_cannot_reconcile_terminal_event_again(self):
        event = self.delta.observe(snap())
        self.delta.reconcile(event.event_id, "REJECT_CANDIDATE", "not approved", "evidence:1")
        with self.assertRaisesRegex(DeltaError, "EVENT_NOT_UNRESOLVED"):
            self.delta.reconcile(event.event_id, "ACCEPT_CANDIDATE", "second try", "evidence:2")

    def test_accepting_one_candidate_rebases_competitors_to_held(self):
        base = self.delta.observe(snap())
        self.delta.reconcile(base.event_id, "ACCEPT_CANDIDATE", "baseline", "evidence:0")
        one = self.delta.observe(snap("1.1.0", D2))
        two = self.delta.observe(snap("1.2.0", D3))
        self.delta.reconcile(two.event_id, "ACCEPT_CANDIDATE", "selected update", "evidence:2")
        self.assertEqual(self.delta.current("active-profile:work").digest, D3)
        rebased = self.delta.get_event(one.event_id)
        self.assertEqual(rebased.status, DeltaStatus.HELD)
        self.assertEqual(rebased.hold_reason, "COMPETING_CANDIDATE_REQUIRES_REBASE")
        self.assertIn("newly confirmed current snapshot", rebased.open_questions[-1])

    def test_non_string_reconciliation_decision_fails_closed(self):
        event = self.delta.observe(snap())
        with self.assertRaisesRegex(DeltaError, "INVALID_RECONCILIATION_DECISION"):
            self.delta.reconcile(event.event_id, [], "no", "evidence:1")

    def test_runtime_delta_event_matches_export_schema(self):
        event = self.delta.observe(snap())
        schema = json.loads((ROOT / "schemas/delta_event.schema.json").read_text(encoding="utf-8"))
        payload = json.loads(json.dumps(asdict(event)))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_invalid_snapshot_digest_rejected(self):
        with self.assertRaisesRegex(DeltaError, "INVALID_DIGEST"):
            self.delta.observe(Snapshot("x", "1.0", "bad", "source:x"))


if __name__ == "__main__":
    unittest.main()
