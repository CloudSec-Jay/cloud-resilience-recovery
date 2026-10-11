# Cloud Resilience & Recovery

Recovery engineering that turns backup configuration into measured restoration evidence.

The initial scaffold models protection and periodic restore testing for an Amazon EBS volume with AWS Backup, based on the recovery pattern already present in Dragonwilds. It separates four questions that are often collapsed into “the backup succeeded”:

1. Was a recovery point created inside the required RPO window?
2. Could AWS restore the resource into an isolated test scope?
3. Did validation prove the restored data and service were usable?
4. Did the entire recovery complete inside the required RTO?

This repository contains reusable recovery objectives, scaffolded CloudFormation, an EBS restore-drill procedure, a scorecard generator, and a dedicated [GitHub Pages case study](https://cloudsec-jay.github.io/cloud-resilience-recovery/). No deployment or completed restore test is claimed until real evidence is added.

## What belongs here

| Area | Source of truth |
|---|---|
| Recovery objectives and definitions | [`recovery-objectives/`](recovery-objectives/) |
| Reusable AWS Backup and restore-testing infrastructure | [`cloudformation/`](cloudformation/) |
| Generic restore and game-day procedure | [`runbooks/`](runbooks/) |
| Sanitized recovery-test records | [`evidence/`](evidence/) |
| RTO/RPO calculation and reporting | [`tools/`](tools/) |

## What remains in workload repositories

Cloud Operations Engineering remains the portfolio and operational hub. Individual workloads keep the instructions that only make sense for that system:

- resource identifiers and deployment wiring;
- application-consistent backup hooks;
- mount, import, and startup ordering;
- workload health checks and integrity assertions;
- rollback procedures and local operational ownership.

For example, Dragonwilds keeps its retained EBS world-volume behavior and controlled save import. This repository owns the reusable recovery method and evidence standard.

## Reference architecture

```text
Protected EBS volume
        │ scheduled backup
        ▼
Encrypted AWS Backup vault
        │ monthly restore test
        ▼
Isolated restored volume
        │ operator validation
        ▼
RTO/RPO scorecard + sanitized evidence
```

The CloudFormation stack deliberately accepts existing backup and restore service-role ARNs. Identity lifecycle stays outside this example so the stack cannot silently create a broad service role.

## Validation

```bash
python3 -m unittest discover -s tools/tests -v
python3 tools/recovery_scorecard.py tools/tests/fixtures/passing-drill.json
cfn-lint cloudformation/backup-foundation.yaml
cfn-guard validate \
  --rules cloudformation/guard/recovery.guard \
  --data cloudformation/backup-foundation.yaml \
  --show-summary fail
```

GitHub Actions runs the unit tests, CloudFormation schema validation, and repository-specific Guard rules. Account-aware validation and deployment require an authenticated non-production AWS account.

## Safety

- Restores can create billable resources. Use a dedicated test account or recovery subnet and tag everything for cleanup.
- Never attach or mount a restored volume over the original source volume.
- Never record account IDs, complete resource ARNs, credentials, private data, or raw application content in public evidence.
- A completed restore job is not a successful recovery until workload validation passes.
- Confirm service-specific backup consistency requirements before generalizing the EBS example to databases or distributed systems.

