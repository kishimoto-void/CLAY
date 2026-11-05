import sys
from pathlib import Path
import unittest
import json
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gamma_index import (EntryStatus, GammaEntry, GammaIndex, GammaIndexError,
                         HoldReason, HoldStatus)

DIGEST = "a" * 64


def entry(entry_id="task.work", digest=DIGEST):
    return GammaEntry(entry_id=entry_id, resource_id="work.general", version="1.0.0",
                      resource_kind="task_profile", scope="current_task_session",
                      content_digest=digest, source_ref="gamma://work.general",
                      source_status="UNVERIFIED", claims=("work profile candidate",),
                      tags=("work", "task"))


class GammaIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = GammaIndex()
        self.index.register(entry())

    def test_register_and_search(self):
        found = self.index.search("work", tags=("task",))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].entry.status, EntryStatus.CANDIDATE)

    def test_hold_preserves_entry_and_claims(self):
        self.index.hold("task.work", "hold-1", HoldReason.INSUFFICIENT_EVIDENCE,
                        ["Is this the intended work profile?"], ["source-ref-1"])
        result = self.index.get("task.work")
        self.assertEqual(result.entry.status, EntryStatus.HELD)
        self.assertEqual(result.entry.claims, ("work profile candidate",))
        self.assertEqual(result.open_holds[0].status, HoldStatus.OPEN)
        self.assertEqual(len(self.index.search(include_held=True)), 1)
        self.assertEqual(len(self.index.search(include_held=False)), 0)

    def test_hold_cannot_be_created_without_question(self):
        with self.assertRaisesRegex(GammaIndexError, "HOLD_REQUIRES_OPEN_QUESTION"):
            self.index.hold("task.work", "hold-1", HoldReason.OTHER, [])

    def test_hold_cannot_close_without_evidence(self):
        self.index.hold("task.work", "hold-1", HoldReason.SOURCE_UNVERIFIED,
                        ["Who supplied this resource?"])
        with self.assertRaisesRegex(GammaIndexError, "HOLD_RESOLUTION_REQUIRES_EVIDENCE"):
            self.index.close_hold("hold-1", EntryStatus.AVAILABLE, "reviewed", "")
        self.assertEqual(self.index.get("task.work").entry.status, EntryStatus.HELD)

    def test_explicit_resolution_closes_hold(self):
        self.index.hold("task.work", "hold-1", HoldReason.SOURCE_UNVERIFIED,
                        ["Who supplied this resource?"])
        hold = self.index.close_hold("hold-1", EntryStatus.AVAILABLE,
                                     "Source verified by host", "host-evidence:123")
        self.assertEqual(hold.status, HoldStatus.CLOSED)
        self.assertEqual(self.index.get("task.work").entry.status, EntryStatus.AVAILABLE)

    def test_duplicate_entry_id_does_not_overwrite(self):
        with self.assertRaisesRegex(GammaIndexError, "ENTRY_ID_COLLISION"):
            self.index.register(entry(digest="b" * 64))
        self.assertEqual(self.index.get("task.work").entry.content_digest, DIGEST)

    def test_resource_version_digest_collision_rejected(self):
        with self.assertRaisesRegex(GammaIndexError, "VERSION_COLLISION"):
            self.index.register(entry(entry_id="other-entry", digest="b" * 64))

    def test_terminal_entry_cannot_be_held(self):
        self.index.close_hold if False else None
        self.index.hold("task.work", "hold-1", HoldReason.OTHER, ["Review?"])
        self.index.close_hold("hold-1", EntryStatus.REJECTED, "Rejected", "evidence:1")
        with self.assertRaisesRegex(GammaIndexError, "TERMINAL_ENTRY_CANNOT_BE_HELD"):
            self.index.hold("task.work", "hold-2", HoldReason.OTHER, ["Reopen?"])

    def test_snapshot_retains_open_hold(self):
        self.index.hold("task.work", "hold-1", HoldReason.MISSING_CONTEXT,
                        ["Need more context"], ["claim:1"])
        snapshot = self.index.snapshot()
        self.assertEqual(snapshot["entries"][0]["status"], "HELD")
        self.assertEqual(snapshot["holds"][0]["status"], "OPEN")

    def test_exact_duplicate_registration_is_idempotent(self):
        replay = self.index.register(entry())
        self.assertEqual(replay.entry_id, "task.work")
        self.assertEqual(len(self.index.search()), 1)

    def test_multiple_open_holds_keep_entry_held_until_all_close(self):
        self.index.hold("task.work", "hold-1", HoldReason.MISSING_CONTEXT, ["Need context A"])
        self.index.hold("task.work", "hold-2", HoldReason.INSUFFICIENT_EVIDENCE, ["Need evidence B"])
        self.index.close_hold("hold-1", EntryStatus.AVAILABLE, "Context reviewed", "evidence:A")
        self.assertEqual(self.index.get("task.work").entry.status, EntryStatus.HELD)
        self.index.close_hold("hold-2", EntryStatus.AVAILABLE, "Evidence reviewed", "evidence:B")
        self.assertEqual(self.index.get("task.work").entry.status, EntryStatus.AVAILABLE)

    def test_register_cannot_forge_terminal_or_held_initial_state(self):
        forged = GammaEntry(entry_id="forged", resource_id="r", version="1.0.0",
                            resource_kind="task_profile", scope="task", content_digest="d" * 64,
                            source_ref="gamma://r", status=EntryStatus.AVAILABLE)
        with self.assertRaisesRegex(GammaIndexError, "INITIAL_STATUS_MUST_BE_CANDIDATE"):
            self.index.register(forged)

    def test_string_is_not_accepted_as_question_iterable(self):
        with self.assertRaisesRegex(GammaIndexError, "HOLD_REQUIRES_QUESTION_LIST"):
            self.index.hold("task.work", "hold-1", HoldReason.OTHER, "What is missing?")

    def test_string_tags_are_not_split_into_characters(self):
        with self.assertRaisesRegex(GammaIndexError, "TAGS_MUST_BE_LIST"):
            self.index.search("work", tags="task")

    def test_runtime_snapshot_matches_export_schema(self):
        self.index.hold("task.work", "hold-schema", HoldReason.OTHER, ["Review this candidate?"])
        schema = json.loads((ROOT / "schemas/gamma_index_snapshot.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(self.index.snapshot()))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_invalid_digest_rejected(self):
        with self.assertRaisesRegex(GammaIndexError, "INVALID_CONTENT_DIGEST"):
            self.index.register(entry(entry_id="bad", digest="not-a-digest"))


if __name__ == "__main__":
    unittest.main()
