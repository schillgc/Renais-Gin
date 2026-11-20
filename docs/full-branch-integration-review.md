# Archived review: `full` branch

**Review date:** 2026-11-20
**Reviewed head:** `384c83533ca54daa614ac84a2bbb5d58fc6d7598`
**Pull request:** [#7](https://github.com/schillgc/Renais-Gin/pull/7), closed without merging

## Outcome

The branch was not merged. It diverged substantially from `master` (41 commits ahead and 37 behind at review) and its tree replaced the established migration history, removed security checks, and included incomplete or simulated integrations. The remote branch was deleted after a full review. No feature from it was ported.

## Reasons for rejecting a wholesale merge

- **Migration history was replaced:** the branch rewrote `0001_initial.py` and removed later migrations, including the default branch's pledge-vote integrity migration. This was not a safe forward migration for existing databases.
- **Security protections regressed:** its changes removed the default branch's security-contract tests and CI workflows.
- **External integrations were not real:** AI behavior was heuristic or placeholder code; blockchain behavior was mock-based; rebate processing simulated transactions.
- **Authorization and API behavior were incomplete:** pledge validation exposed mock behavior and did not provide a complete, authorized community-review workflow.
- **Background processing was not deployable:** task code depended on broker/worker services that were not configured as a complete deployment.
- **User-facing dashboards overstated data:** some views rendered hard-coded sample stories or counters, and the movement dashboard expected metric names not returned by the real endpoint.
- **Deployment configuration was inconsistent:** settings, dependencies, Docker configuration, and referenced infrastructure did not form a verified deployment.

## Porting guidance

No complete, distinct feature met the bar for porting. Equivalent bottle, pledge, review, circle, metrics, and account workflows are already implemented on `master`. Any future API, async-task, or dashboard work should be designed and tested directly against the current models, authorization rules, settings, and migrations. Do not copy the branch's payment, AI, or blockchain claims into product documentation.

This record documents the decision only. It does not establish production readiness, endorse product or impact claims, or replace vulnerability reporting guidance in [SECURITY.md](../SECURITY.md).
