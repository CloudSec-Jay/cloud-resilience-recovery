# EBS restore-testing drill

This runbook validates the reference AWS Backup design in a non-production account. Replace placeholders through reviewed deployment inputs; do not commit account-specific values.

## Preconditions

- Approved maintenance and test window
- Known RTO and RPO targets
- Existing least-privilege AWS Backup and restore service roles
- Encrypted EBS volume selected for the lab
- Recovery subnet or isolated validation host available
- Owner for cleanup and cost verification
- Baseline file manifest or application-specific integrity test

## 1. Confirm protection

1. Verify the protected volume ARN is the exact intended target.
2. Confirm the backup plan, vault, schedule, retention, and KMS key.
3. Confirm at least one completed recovery point exists within the RPO window.
4. Record sanitized identifiers: stack commit, plan version, recovery-point creation time, and test ticket.

Stop if the recovery point is outside the RPO target or its encryption and ownership cannot be verified.

## 2. Start the restore test

Prefer the scheduled AWS Backup restore-testing plan. For an approved manual drill, start the plan through the AWS Backup console or API and record the job start time.

The restored volume must be a new resource. Do not replace or attach over the source volume.

## 3. Validate the restored resource

1. Confirm the restore job completed and the volume is encrypted.
2. Attach the restored volume to an isolated validation instance using an unused device mapping.
3. Mount the filesystem read-only first.
4. Run the workload-specific manifest, database, or application integrity check.
5. If write testing is required, create a disposable clone or receive explicit approval before remounting read-write.
6. Record the time validation completed and whether every required check passed.

AWS Backup job completion alone does not satisfy this step.

## 4. Calculate results

Create a sanitized drill record from [`../evidence/recovery-test-template.json`](../evidence/recovery-test-template.json), then run:

```bash
python3 tools/recovery_scorecard.py path/to/drill.json
```

Store raw logs and screenshots in the approved protected evidence system. Commit only the sanitized scorecard or evidence reference.

## 5. Cleanup and recovery

1. Unmount and detach the restored volume.
2. Delete the temporary restored volume after evidence is retained and cleanup is approved.
3. Remove temporary validation infrastructure created only for the drill.
4. Confirm no source resource was changed.
5. Review cost and tag reports for orphaned resources.
6. Open follow-up work for missed objectives, failed checks, or manual bottlenecks.

