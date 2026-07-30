# Historical trigger-only Factory Runtime rerun

Classification: historical, non-active fixture.

This directory preserves the exact root `.factory/` tree and `opencode.json`
used by the 2026-07-29 trigger-only rerun. They were relocated together so
Factory Runtime and OpenCode cannot auto-discover them from the Factory Test
repository root.

The bundle stops after Review, contains stale workstation paths, and pins an
obsolete worker/model selection. It is retained for provenance only. It must
not be executed as current Commons configuration, used as acceptance evidence,
or treated as the canonical Intake-through-Ship pipeline.

Current acceptance design lives in `acceptance/commons.factory.v1/`; controlled
event conformance fixtures live in `fixtures/commons.factory.evaluation.v1/`.
