# Dakarli AI — Verified Real Tool Traces

This directory contains traces captured from actual tool interactions, not synthetic descriptions of what a tool might return.

## Trace lifecycle

Each trace records:

`request -> plan -> tool_call -> real_observation -> decision -> correction -> verification`

A trace may omit stages that were not needed, but it must never invent an observation or claim a side effect that did not occur.

## Source policy

- `verified_connector`: observation came from an actual connected GitHub operation.
- `verified_runtime`: observation came from an executed sandbox/runtime operation.
- `verified_browser`: observation came from an actual browser session.
- `synthetic`: scenario only; never mix this into the verified-real tier.

Synthetic examples belong in the normal generated dataset. They must not be labeled as real traces.

## Required fields

- `trace_id`
- `source_type`
- `tool`
- `request`
- `steps`
- `outcome`
- `verification`
- `quality`

## Quality gates

1. Every tool call has structured arguments.
2. Every observation is copied or summarized from the actual tool result.
3. Failed calls are preserved rather than silently removed.
4. Corrections reference the failed step.
5. Verification is a separate step from the action.
6. Secrets, tokens, private user data, and credentials are excluded.

The current verified tier starts with GitHub traces because GitHub is the connected execution surface available to this repository pipeline. Browser, terminal, Vercel, Supabase, and Search Console traces must only be added after their real execution integrations are available.