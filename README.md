# Dakarli AI

Production-oriented training and evaluation stack for a specialized Web/SEO/Programming/UX/Agent model.

## Dataset V2.2

The repository now uses a structured dataset pipeline covering:

- SFT: SEO, programming, UX/UI, Supabase/Postgres, RAG, agents
- Tool calling: GitHub, terminal, browser, Vercel, Supabase, Search Console
- Agent trajectories: plan → tool call → observation → correction → verification
- Debugging and SEO audit cases
- Negative/safety/permission cases
- Held-out evaluation benchmark

The dataset generator is deterministic and creates thousands of structured examples from curated scenario families. Generated artifacts are written under `data/generated/` and should not be edited manually.

## Generate

```bash
python scripts/build_dataset.py --output data/generated --target 10000 --seed 42
python scripts/validate_dataset.py data/generated
```

## Principle

Dakarli AI must learn reliable behavior, not just a writing style. Training data therefore includes tool schemas, expected tool calls, observations, corrections, verification steps, permission boundaries, and explicit refusal of unsupported claims.
