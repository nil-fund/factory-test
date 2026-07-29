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

`b712e46532403e43c4bbf1850809d171bd228e783c8e828ec6e012cad57b0fa6`

Three expected-fail fixtures preserve lifecycle gaps found in the frozen
pre-relocation validator:

- `invalid/ship-after-failed-post-merge-gate.jsonl`
- `invalid/repeated-merge-stage-advancement.jsonl`
- `invalid/failed-completion-stale-causal-parent.jsonl`

The Gates-owned record-conformance control closes those gaps and must reject
all three. Accepting any indexed `fail` fixture is `BLOCK`.

The normative schema, lifecycle reducer, and conformance command belong to
Gates. Episodic stores append-only experience records only. Factory Runtime may
preflight a prospective stream, but conformance does not prove that a gate ran,
that provider evidence is authentic, or that a Commons success criterion was
achieved.

Run this corpus through the reviewed Gates control; do not implement a second
validator here. Success-criteria fixtures and evidence manifests may build on
this corpus, but missing evidence remains invalid rather than passing.
