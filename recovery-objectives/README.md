# Recovery objectives

Recovery objectives must be defined before selecting retention, schedules, or automation.

## Required definitions

| Objective | Meaning | Measured from |
|---|---|---|
| RTO | Maximum acceptable time to restore usable service | Incident declaration to validated service restoration |
| RPO | Maximum acceptable data loss expressed as time | Incident declaration back to the newest validated recovery point |
| MTD | Maximum tolerable disruption before unacceptable impact | Business-impact analysis, not tool capability |
| Retention | How long recovery points remain available | Legal, operational, and investigation requirements |

## Example lab target

The included EBS exercise uses illustrative—not production-approved—targets:

- RTO: 120 minutes
- RPO: 24 hours
- Backup retention: 35 days
- Restore test: monthly
- Validation window: 24 hours

These values are intentionally easy to identify and replace. A workload owner must approve objectives based on impact and measured restoration behavior.

## Measurement rules

- Start the RTO clock when the incident is declared, not when an operator begins restoration.
- Stop the RTO clock only after the restored workload passes its defined health and integrity checks.
- Calculate RPO from the incident time to the creation time of the newest recovery point proven usable.
- Report queued time, restore time, validation time, and operator decision time separately when available.
- A missed target is evidence for design improvement, not a reason to alter timestamps or redefine the objective after the drill.

