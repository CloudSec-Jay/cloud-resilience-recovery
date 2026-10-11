import unittest

from tools.recovery_scorecard import build_scorecard, parse_timestamp, render_markdown


def example_record():
    return {
        "drill_id": "test-drill",
        "incident_declared_at": "2026-01-15T14:00:00Z",
        "recovery_point_created_at": "2026-01-15T02:00:00Z",
        "restore_started_at": "2026-01-15T14:10:00Z",
        "resource_restored_at": "2026-01-15T14:48:00Z",
        "validation_completed_at": "2026-01-15T15:05:00Z",
        "rto_target_minutes": 120,
        "rpo_target_minutes": 1440,
        "validation_passed": True,
    }


class RecoveryScorecardTests(unittest.TestCase):
    def test_passing_drill(self):
        scorecard = build_scorecard(example_record())
        self.assertEqual(scorecard["rto_minutes"], 65)
        self.assertEqual(scorecard["rpo_minutes"], 720)
        self.assertTrue(scorecard["rto_met"])
        self.assertTrue(scorecard["rpo_met"])

    def test_validation_failure_fails_objectives(self):
        record = example_record()
        record["validation_passed"] = False
        scorecard = build_scorecard(record)
        self.assertFalse(scorecard["rto_met"])
        self.assertFalse(scorecard["rpo_met"])

    def test_rejects_out_of_order_timestamps(self):
        record = example_record()
        record["resource_restored_at"] = "2026-01-15T14:05:00Z"
        with self.assertRaises(ValueError):
            build_scorecard(record)

    def test_rejects_timestamp_without_timezone(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2026-01-15T14:00:00")

    def test_markdown_contains_results(self):
        rendered = render_markdown(build_scorecard(example_record()))
        self.assertIn("| RTO | 65.0 min", rendered)
        self.assertIn("| RPO | 720.0 min", rendered)


if __name__ == "__main__":
    unittest.main()

