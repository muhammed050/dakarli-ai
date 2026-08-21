# Dakarli Dataset V2.2

## Goal

The dataset teaches reliable behavior rather than a superficial response style. Every family is designed around a measurable capability.

### SFT

- SEO technical
- SEO content reasoning
- Programming and debugging
- UX/UI and accessibility
- Supabase/Postgres
- RAG and grounding
- Agent planning

### Tool calling

Examples cover read-only tools, workspace edits, sandbox tests, external browser interactions, deployments, database writes, and Search Console queries. Tool risk and required approval are explicit.

### Agent trajectories

Each trajectory follows:

`plan -> tool_call -> observation -> correction -> verification`

A trajectory is considered incomplete if it claims success without evidence or ignores a failed verification step.

### Negative / safety

Examples teach the model to refuse destructive or out-of-scope actions, protect secrets, and ask for approval before high-impact operations.

## Dataset policy

1. Never put real credentials, private user data, or production secrets in training data.
2. Keep evaluation examples isolated from training examples.
3. Prefer executable/verifiable outcomes over subjective claims.
4. Preserve tool arguments and observations as structured data when possible.
5. Do not treat synthetic examples as evidence of real-world tool execution.
6. Re-run the validator whenever dataset generation changes.

## Current build target

The CI pipeline deterministically generates **10,000 examples** from curated scenario families with a fixed seed and validates uniqueness, roles, splits, task taxonomy, and quality metadata.
