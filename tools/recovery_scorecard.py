"""Calculate RTO and RPO from a sanitized recovery-drill record."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "drill_id",
    "incident_declared_at",
    "recovery_point_created_at",
    "restore_started_at",
    "resource_restored_at",
    "validation_completed_at",
    "rto_target_minutes",
    "rpo_target_minutes",
    "validation_passed",
)


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and require an explicit timezone."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a timezone: {value}")
    return parsed


def minutes_between(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 60, 2)


def build_scorecard(record: dict[str, Any]) -> dict[str, Any]:
    """Validate a drill record and return measured recovery outcomes."""
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    incident = parse_timestamp(record["incident_declared_at"])
    recovery_point = parse_timestamp(record["recovery_point_created_at"])
    restore_started = parse_timestamp(record["restore_started_at"])
    restored = parse_timestamp(record["resource_restored_at"])
    validated = parse_timestamp(record["validation_completed_at"])

    if not recovery_point <= incident <= restore_started <= restored <= validated:
        raise ValueError("timestamps are not in the expected recovery sequence")

    rto = minutes_between(incident, validated)
    rpo = minutes_between(recovery_point, incident)
    restore_duration = minutes_between(restore_started, restored)
    validation_duration = minutes_between(restored, validated)
    validation_passed = record["validation_passed"] is True

    return {
        "drill_id": record["drill_id"],
        "rto_minutes": rto,
        "rto_target_minutes": record["rto_target_minutes"],
        "rto_met": validation_passed and rto <= record["rto_target_minutes"],
        "rpo_minutes": rpo,
        "rpo_target_minutes": record["rpo_target_minutes"],
        "rpo_met": validation_passed and rpo <= record["rpo_target_minutes"],
        "restore_duration_minutes": restore_duration,
        "validation_duration_minutes": validation_duration,
        "validation_passed": validation_passed,
        "evidence_reference": record.get("evidence_reference", "not recorded"),
    }


def render_markdown(scorecard: dict[str, Any]) -> str:
    def result(value: bool) -> str:
        return "PASS" if value else "FAIL"

    return "\n".join(
        (
            f"# Recovery scorecard: {scorecard['drill_id']}",
            "",
            "| Measure | Observed | Target | Result |",
            "|---|---:|---:|---|",
            f"| RTO | {scorecard['rto_minutes']} min | {scorecard['rto_target_minutes']} min | {result(scorecard['rto_met'])} |",
            f"| RPO | {scorecard['rpo_minutes']} min | {scorecard['rpo_target_minutes']} min | {result(scorecard['rpo_met'])} |",
            f"| Restore duration | {scorecard['restore_duration_minutes']} min | — | Recorded |",
            f"| Validation duration | {scorecard['validation_duration_minutes']} min | — | Recorded |",
            f"| Workload validation | — | Required | {result(scorecard['validation_passed'])} |",
            "",
            f"Evidence reference: `{scorecard['evidence_reference']}`",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an RTO/RPO scorecard from a sanitized recovery drill")
    parser.add_argument("record", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        scorecard = build_scorecard(record)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"scorecard error: {error}\n")

    if args.as_json:
        print(json.dumps(scorecard, indent=2, sort_keys=True))
    else:
        print(render_markdown(scorecard))
    return 0 if scorecard["rto_met"] and scorecard["rpo_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

