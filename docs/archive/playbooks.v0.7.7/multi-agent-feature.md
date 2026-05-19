# Playbook: Multi-Agent Feature

Use this playbook when a feature is large enough to split across agents.

## Flow

1. Define the goal and terminal criteria.
2. Identify affected module contracts.
3. Create task contracts for PR-sized slices.
4. Add dependencies where write scopes or surfaces conflict.
5. Generate context packs for ready tasks.
6. Dispatch agents only for non-overlapping tasks.
7. Collect proof and handoff output.
8. Run review contracts.
9. Convert blocking findings into task contracts.
10. Integrate accepted slices through an integration contract.
11. Run final proof and record terminal status.

## Stop Conditions

Stop and report blocker evidence when:

- no readiness oracle exists;
- proof cannot be defined;
- agents require overlapping writes without a dependency order;
- a human decision is required;
- budget or policy prevents safe completion.
