# Commons Factory evaluation v1 corpus

This is the controlled conformance corpus for the Commons Factory evaluation
event contract.

- `valid/` contains seven complete JSONL streams whose expected result is
  `pass`.
- `invalid/` contains seventy-six focused counterexamples whose expected
  result is `fail`.
- `index.tsv` is the exact, byte-bound corpus index. Each tab-separated row is
  `expected_result`, validation mode, repository-relative fixture path, and
  SHA-256 of the fixture bytes. Rows are the exact recursive, symlink-free
  inventory and are ordered by repository-relative path using the C locale.
  `stream` invokes record conformance for JSONL, `schema_only` invokes
  non-authoritative producer preflight for a deliberately malformed standalone
  event, and `authoritative` proves that a schema-valid dependent singleton
  cannot establish stream causality.

The deterministic corpus digest is the SHA-256 of the complete `index.tsv`
bytes:

`a3bf8292254a72baa70aae90fb888166f194676e603c8af4c7b8b676536e4913`

Four expected-fail fixtures preserve lifecycle gaps found in the frozen
pre-relocation validator:

- `invalid/ship-after-failed-post-merge-gate.jsonl`
- `invalid/repeated-merge-stage-advancement.jsonl`
- `invalid/failed-completion-stale-causal-parent.jsonl`
- `invalid/ship-parent-bypasses-ship-gate.jsonl`

The Gates-owned record-conformance control closes those gaps and must reject
all four. Accepting any indexed `fail` fixture is `BLOCK`.

All unrelated fixtures use a coherent chronological and aggregate-metric
baseline. A fixture reaches its named boundary without accidentally failing
first on a future-dated provider verification, regressing append time,
fabricated completion total, or stale baseline causal edge.

The normative schema, lifecycle reducer, and conformance command belong to
Gates. Episodic stores append-only experience records only. Factory Runtime may
preflight a prospective stream, but conformance proves neither that a gate ran
nor that gate, cost, or provider evidence is authentic, and it cannot prove that
a Commons success criterion was achieved.

Run this corpus through the reviewed Gates control; do not implement a second
validator here. Success-criteria fixtures and evidence manifests may build on
this corpus, but missing evidence remains invalid rather than passing.
